# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_document import TenderBidDocumentResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="belowThreshold:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender bidder documents",
)
class BelowThresholdTenderBidDocumentResource(TenderBidDocumentResource):
    pass
