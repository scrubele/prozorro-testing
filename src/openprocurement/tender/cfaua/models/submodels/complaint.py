# -*- coding: utf-8 -*-
from openprocurement.api.models import ListType
from openprocurement.tender.core.models import (
    ComplaintModelType as BaseComplaintModelType,
    get_tender,
    Complaint as BaseComplaint,
    EUDocument,
)
from schematics.types.compound import ModelType
from schematics.types import StringType, BooleanType
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from openprocurement.api.models import IsoDateTimeType
from pyramid.security import Allow


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = [
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
    ]


class Complaint(BaseComplaint):
    class Options:
        _view_claim = whitelist(
            'acceptance', 'bid_id', 'cancellationReason', 'complaintID', 'date', 'dateAccepted',
            'dateAnswered', 'dateCanceled', 'dateDecision', 'dateEscalated', 'dateSubmitted', 'decision',
            'description', 'documents', 'id', 'rejectReason', 'rejectReasonDescription', 'relatedLot', 'resolution',
            'resolutionType', 'reviewDate', 'reviewPlace', 'satisfied', 'status', 'tendererAction',
            'tendererActionDate', 'title', 'type',
        )
        _open_view = _view_claim + whitelist('author')
        _embedded = _open_view - whitelist('bid_id')  # "-bid_id" looks like a typo in the original csv
        roles = {
            "view_claim": _view_claim,
            "active.enquiries": _open_view,
            "active.tendering": _open_view,
            "active.pre-qualification": _open_view,
            "active.pre-qualification.stand-still": _open_view,
            "active.auction": _open_view,
            "active.qualification": _open_view,
            "active.qualification.stand-still": _open_view,
            "active.awarded": _open_view,
            "complete": _open_view,
            "unsuccessful": _open_view,
            "cancelled": _open_view,
            "embedded": _embedded,
            "view": _embedded,
            "default": _open_view + whitelist('owner', 'owner_token'),

            "create": whitelist('author', 'description', 'status', 'title', 'relatedLot'),
            "draft": whitelist('author', 'description', 'status', 'title'),
            "review": whitelist('decision', 'reviewDate', 'reviewPlace', 'status'),
            "answer": whitelist('resolution', 'resolutionType', 'status', 'tendererAction'),
            "pending": whitelist('decision', 'rejectReason', 'rejectReasonDescription', 'status'),
            "satisfy": whitelist('satisfied', 'status'),
            "escalate": whitelist('status'),
            "resolve": whitelist('status', 'tendererAction'),
            "action": whitelist('tendererAction'),
            "cancellation": whitelist('cancellationReason', 'status'),
        }

    documents = ListType(ModelType(EUDocument, required=True), default=list())
    status = StringType(
        choices=[
            "draft",
            "claim",
            "answered",
            "pending",
            "accepted",
            "invalid",
            "resolved",
            "declined",
            "cancelled",
            "satisfied",
            "stopping",
            "stopped",
            "mistaken",
        ],
        default="draft",
    )
    acceptance = BooleanType()
    dateAccepted = IsoDateTimeType()
    rejectReason = StringType(choices=["lawNonСompliance", "noPaymentReceived", "buyerViolationsСorrected"])
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()
    bid_id = StringType()

    def __acl__(self):
        return [
            (Allow, "g:aboveThresholdReviewers", "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_complaint_documents"),
        ]

    def get_role(self):
        root = self.get_root()
        request = root.request
        data = request.json_body["data"]
        if request.authenticated_role == "complaint_owner" and data.get("status", self.status) == "cancelled":
            role = "cancellation"
        elif (
            request.authenticated_role == "complaint_owner"
            and self.status in ["pending", "accepted"]
            and data.get("status", self.status) == "stopping"
        ):
            role = "cancellation"
        elif request.authenticated_role == "complaint_owner" and self.status == "draft":
            role = "draft"
        elif request.authenticated_role == "complaint_owner" and self.status == "claim":
            role = "escalate"
        elif request.authenticated_role == "tender_owner" and self.status == "claim":
            role = "answer"
        elif request.authenticated_role == "tender_owner" and self.status in ["pending", "accepted"]:
            role = "action"
        elif request.authenticated_role == "tender_owner" and self.status == "satisfied":
            role = "resolve"
        elif request.authenticated_role == "complaint_owner" and self.status == "answered":
            role = "satisfy"
        elif request.authenticated_role == "aboveThresholdReviewers" and self.status == "pending":
            role = "pending"
        elif request.authenticated_role == "aboveThresholdReviewers" and self.status in ["accepted", "stopping"]:
            role = "review"
        else:
            role = "invalid"
        return role

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get("status") in ["cancelled", "stopping"]:
            raise ValidationError(u"This field is required.")

    def serialize(self, role=None, context=None):
        if (
            role == "view"
            and self.type == "claim"
            and get_tender(self).status
            in [
                "active.tendering",
                "active.pre-qualification",
                "active.pre-qualification.stand-still",
                "active.auction",
            ]
        ):
            role = "view_claim"
        return super(Complaint, self).serialize(role=role, context=context)
