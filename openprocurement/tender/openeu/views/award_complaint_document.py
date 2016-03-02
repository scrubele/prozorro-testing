# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_complaint_document import TenderUaAwardComplaintDocumentResource


@opresource(name='Tender EU Award Complaint Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender award complaint documents")
class TenderEUAwardComplaintDocumentResource(TenderUaAwardComplaintDocumentResource):
    pass
