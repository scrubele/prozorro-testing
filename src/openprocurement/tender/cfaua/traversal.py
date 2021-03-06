# -*- coding: utf-8 -*-
from openprocurement.tender.core.traversal import Root, get_item, handle_root


def qualifications_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("qualification_id"):
        qualification = get_item(tender, "qualification", request)
        if request.matchdict.get("complaint_id"):
            complaint = get_item(qualification, "complaint", request)
            if request.matchdict.get("document_id"):
                return get_item(complaint, "document", request)
            else:
                return complaint
        elif request.matchdict.get("document_id"):
            return get_item(qualification, "document", request)
        else:
            return qualification
    request.validated["id"] = request.matchdict["tender_id"]
    return tender


def agreement_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("agreement_id"):
        agreement = get_item(tender, "agreement", request)
        if request.matchdict.get("change_id"):
            change = get_item(agreement, "change", request)
            return change
        elif request.matchdict.get("document_id"):
            return get_item(agreement, "document", request)
        elif request.matchdict.get("contract_id"):
            return get_item(agreement, "contract", request)
        else:
            return agreement
    request.validated["id"] = request.matchdict["tender_id"]
    return tender


def get_document(parent, key, request):
    request.validated["document_id"] = request.matchdict["document_id"]

    attr = key.split("_")
    attr = attr[0] + attr[1].capitalize() + "s"
    items = [i for i in getattr(parent, attr, []) if i.id == request.matchdict["document_id"]]
    if not items:
        from openprocurement.api.utils import error_handler

        request.errors.add("url", "document_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)
    else:
        if "document" in key:
            request.validated["documents"] = items
        item = items[-1]
        request.validated["document"] = item

        request.validated["id"] = request.matchdict["document_id"]
        item.__parent__ = parent
        return item


def bid_financial_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("bid_id"):
        bid = get_item(tender, "bid", request)
        if request.matchdict.get("document_id"):
            return get_document(bid, "financial_document", request)
        else:
            return bid


def bid_eligibility_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("bid_id"):
        bid = get_item(tender, "bid", request)
        if request.matchdict.get("document_id"):
            return get_document(bid, "eligibility_document", request)
        else:
            return bid


def bid_qualification_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated["tender"]
    if request.matchdict.get("bid_id"):
        bid = get_item(tender, "bid", request)
        if request.matchdict.get("document_id"):
            return get_document(bid, "qualification_document", request)
        else:
            return bid
