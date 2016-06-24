# -*- coding: utf-8 -*-
import unittest
from email.header import Header
from openprocurement.planning.api.tests.base import BasePlanWebTest


class PlanDocumentResourceTest(BasePlanWebTest):
    docservice = False

    def test_not_found(self):
        response = self.app.get('/plans/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'plan_id'}
        ])

        response = self.app.post('/plans/some_id/documents', status=404, upload_files=[
                                 ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'plan_id'}
        ])

        response = self.app.post('/plans/{}/documents'.format(self.plan_id), status=404, upload_files=[
                                 ('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/plans/some_id/documents/some_id', status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'plan_id'}
        ])

        response = self.app.put('/plans/{}/documents/some_id'.format(
            self.plan_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])
        
        response = self.app.get('/plans/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'plan_id'}
        ])

        response = self.app.get('/plans/{}/documents/some_id'.format(
            self.plan_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_plan_document(self):
        response = self.app.get('/plans/{}/documents'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json, {"data": []})

        response = self.app.post('/plans/{}/documents'.format(
            self.plan_id), upload_files=[('file', u'укр.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            plan = self.db.get(self.plan_id)
            self.assertIn(key, plan['documents'][-1]["url"])
            self.assertIn('Signature=', plan['documents'][-1]["url"])
            self.assertIn('KeyID=', plan['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/plans/{}/documents'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

        response = self.app.get('/plans/{}/documents/{}?download=some_id'.format(
            self.plan_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        if self.docservice:
            response = self.app.get('/plans/{}/documents/{}?download={}'.format(
                self.plan_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/plans/{}/documents/{}?download={}'.format(
                self.plan_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        response = self.app.get('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        response = self.app.post('/plans/{}/documents?acc_token=acc_token'.format(
            self.plan_id), upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertNotIn('acc_token', response.headers['Location'])

    def test_put_plan_document(self):
        from six import BytesIO
        from urllib import quote
        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n'''.format(u'\uff07')
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/plans/{}/documents'.format(self.plan_id)), environ)
        req.environ['wsgi.input'] = BytesIO(body.encode('utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "could not decode params")

        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n'''.format(quote('укр.doc'))
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/plans/{}/documents'.format(self.plan_id)), environ)
        req.environ['wsgi.input'] = BytesIO(body.encode(req.charset or 'utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req)
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id), upload_files=[('file', 'name  name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            plan = self.db.get(self.plan_id)
            self.assertIn(key, plan['documents'][-1]["url"])
            self.assertIn('Signature=', plan['documents'][-1]["url"])
            self.assertIn('KeyID=', plan['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        if self.docservice:
            response = self.app.get('/plans/{}/documents/{}?download={}'.format(
                self.plan_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/plans/{}/documents/{}?download={}'.format(
                self.plan_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        response = self.app.get('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name name.doc', response.json["data"]["title"])
        dateModified2 = response.json["data"]['dateModified']
        self.assertTrue(dateModified < dateModified2)
        self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])

        response = self.app.get('/plans/{}/documents?all=true'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

        response = self.app.post('/plans/{}/documents'.format(
            self.plan_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.get('/plans/{}/documents'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

        response = self.app.put('/plans/{}/documents/{}'.format(self.plan_id, doc_id), status=404, upload_files=[
                                ('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            plan = self.db.get(self.plan_id)
            self.assertIn(key, plan['documents'][-1]["url"])
            self.assertIn('Signature=', plan['documents'][-1]["url"])
            self.assertIn('KeyID=', plan['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        if self.docservice:
            response = self.app.get('/plans/{}/documents/{}?download={}'.format(
                self.plan_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/plans/{}/documents/{}?download={}'.format(
                self.plan_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

    def test_patch_plan_document(self):
        response = self.app.post('/plans/{}/documents'.format(
            self.plan_id), upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        self.assertNotIn("documentType", response.json["data"])

        response = self.app.patch_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id), {"data": {
            "description": "document description",
            "documentType": 'notice'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'notice')

        response = self.app.patch_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id), {"data": {
            "documentType": None
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertNotIn("documentType", response.json["data"])

        response = self.app.get('/plans/{}/documents/{}'.format(self.plan_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])


class PlanDocumentWithDSResourceTest(PlanDocumentResourceTest):
    docservice = True

    def test_create_plan_document_json_invalid(self):
        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'format': 'application/msword',
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "This field is required.")

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': 'http://invalid.docservice.url/get/uuid',
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': '/'.join(self.generate_docservice_url().split('/')[:4]),
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url().split('?')[0],
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url().replace(self.app.app.registry.keyring.keys()[-1], '0' * 8),
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Document url expired.")

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url().replace("Signature=", "Signature=ABC"),
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Document url signature invalid.")

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url().replace("Signature=", "Signature=bw%3D%3D"),
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Document url invalid.")

    def test_create_plan_document_json(self):
        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        plan = self.db.get(self.plan_id)
        self.assertIn(key, plan['documents'][-1]["url"])
        self.assertIn('Signature=', plan['documents'][-1]["url"])
        self.assertIn('KeyID=', plan['documents'][-1]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])

        response = self.app.get('/plans/{}/documents'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

        response = self.app.get('/plans/{}/documents/{}?download=some_id'.format(
            self.plan_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/plans/{}/documents/{}?download={}'.format(
            self.plan_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)

        response = self.app.get('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertNotIn('acc_token', response.headers['Location'])

    def test_put_plan_document_json(self):
        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        datePublished = response.json["data"]['datePublished']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id),
            {'data': {
                'title': u'name.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        plan = self.db.get(self.plan_id)
        self.assertIn(key, plan['documents'][-1]["url"])
        self.assertIn('Signature=', plan['documents'][-1]["url"])
        self.assertIn('KeyID=', plan['documents'][-1]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])

        response = self.app.get('/plans/{}/documents/{}?download={}'.format(
            self.plan_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)

        response = self.app.get('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        dateModified2 = response.json["data"]['dateModified']
        self.assertTrue(dateModified < dateModified2)
        self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
        self.assertEqual(response.json["data"]['datePublished'], datePublished)

        response = self.app.get('/plans/{}/documents?all=true'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id, doc_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.get('/plans/{}/documents'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

        response = self.app.put_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        plan = self.db.get(self.plan_id)
        self.assertIn(key, plan['documents'][-1]["url"])
        self.assertIn('Signature=', plan['documents'][-1]["url"])
        self.assertIn('KeyID=', plan['documents'][-1]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])

        response = self.app.get('/plans/{}/documents/{}?download={}'.format(
            self.plan_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)

        self.set_status('active.planing')

        response = self.app.put_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id),
            {'data': {
                'title': u'укр.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.planing) plan status")

    def test_put_plan_document_json(self):
        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'name name.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'name name.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id),
            {'data': {
                'title': u'name.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        plan = self.db.get(self.plan_id)
        self.assertIn(key, plan['documents'][-1]["url"])
        self.assertIn('Signature=', plan['documents'][-1]["url"])
        self.assertIn('KeyID=', plan['documents'][-1]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])

        response = self.app.get('/plans/{}/documents/{}?download={}'.format(
            self.plan_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)

        response = self.app.get('/plans/{}/documents/{}'.format(
            self.plan_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name name.doc', response.json["data"]["title"])
        dateModified2 = response.json["data"]['dateModified']
        self.assertTrue(dateModified < dateModified2)
        self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])

        response = self.app.get('/plans/{}/documents?all=true'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

        response = self.app.post_json('/plans/{}/documents'.format(self.plan_id),
            {'data': {
                'title': u'name.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.get('/plans/{}/documents'.format(self.plan_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

        response = self.app.put_json('/plans/{}/documents/{}'.format(self.plan_id, doc_id),
            {'data': {
                'title': u'name.doc',
                'url': self.generate_docservice_url(),
                'md5': '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        plan = self.db.get(self.plan_id)
        self.assertIn(key, plan['documents'][-1]["url"])
        self.assertIn('Signature=', plan['documents'][-1]["url"])
        self.assertIn('KeyID=', plan['documents'][-1]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])

        response = self.app.get('/plans/{}/documents/{}?download={}'.format(
            self.plan_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PlanDocumentResourceTest))
    suite.addTest(unittest.makeSuite(PlanDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
