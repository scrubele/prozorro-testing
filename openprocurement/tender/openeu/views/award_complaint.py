# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_complaint import TenderUaAwardComplaintResource


@opresource(name='Tender EU Award Complaints',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU award complaints")
class TenderEUAwardComplaintResource(TenderUaAwardComplaintResource):
    pass
