# import os
# import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
# from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.content.browser.interfaces import IFolderContentsView
# from plone.app.layout.globals.interfaces import IViewView
# from zope.interface import implements

#from Products.Five.browser import BrowserView
from bika.lims.browser import BrowserView
# from bika.lims.browser.bika_listing import BikaListingView
# from bika.lims.browser.multifile import MultifileView
# from bika.lims.utils import to_utf8
# from baobab.lims import bikaMessageFactory as _
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.utils.local_server_time import getLocalServerTime

import json


class CollectionRequestView(BrowserView):
    template = ViewPageTemplateFile('templates/collectionrequest_view.pt')

    def __init__(self, context, request):
        super(CollectionRequestView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.collection_request_uid = self.context.UID()

        # self.title = self.context.Title()
        # self.description = self.context.Description()
        self.client = self.get_client(self.context)
        self.request_number = self.context.getRequestNumber()
        self.sample_kingdom = self.get_sample_kingdom(self.context)
        self.number_requested = self.context.getNumberRequested()
        self.date_evaluated= self.context.getDateEvaluated()
        self.result_of_evaluation= self.context.getResultOfEvaluation()
        self.reason_for_evaluation= self.context.getReasonForEvaluation()

        self.human_sample_request_rows = self.prepare_human_sample_request_rows()
        self.microbe_sample_request_rows = self.prepare_microbe_sample_request_rows()

        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

    def prepare_human_sample_request_rows(self):

        human_sample_request_rows = self.context.get_human_sample_requests()
        prepared_request_rows = []

        for sample_request in human_sample_request_rows:
            # approved = sample_request.getField('Approved').get(sample_request)
            # approval_status = self.get_approval_status(approved)

            prepared_request = {
                'approved': sample_request.getField('Approved').get(sample_request),
                # 'status_approved': approval_status['approved_status'],
                # 'status_rejected': approval_status['rejected_status'],
                # 'status_unspecified': approval_status['unspecified_status'],
                'barcode': sample_request.getField('Barcode').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'volume': sample_request.getField('Volume').get(sample_request),
                'unit': sample_request.getField('Unit').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    # def get_approval_status(self, approval):
    #     approval_status = {
    #         'rejected_status': False,
    #         'approved_status': False,
    #         'unspecified_status': False,
    #     }
    #
    #     if approval == 'rejected':
    #         approval_status['rejected_status'] = True
    #         return approval_status
    #
    #     if approval == 'approved':
    #         approval_status['approved_status'] = True
    #         return approval_status
    #
    #     approval_status['unspecified_status'] = True
    #     return approval_status

    def prepare_microbe_sample_request_rows(self):

        microbe_sample_request_rows = self.context.get_microbe_sample_requests()
        prepared_request_rows = []

        for sample_request in microbe_sample_request_rows:
            # approved = sample_request.getField('Approved').get(sample_request)
            # approval_status = self.get_approval_status(approved)

            prepared_request = {
                'approved': sample_request.getField('Approved').get(sample_request),
                # 'status_approved': approval_status['approved_status'],
                # 'status_rejected': approval_status['rejected_status'],
                # 'status_unspecified': approval_status['unspecified_status'],
                'identification': sample_request.getField('Identification').get(sample_request),
                'strain': self.get_strain(sample_request),
                'origin': sample_request.getField('Origin').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'phenotype': sample_request.getField('Phenotype').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    def get_client(self, collection_request):
        try:
            client = collection_request.getField('Client').get(collection_request)
            return client.Title()
        except:
            return ''

    def get_sample_kingdom(self, collection_request):
        try:
            sample_kingdom = collection_request.getSampleKingdom()
            return sample_kingdom.Title()
        except:
            return ''


    def get_sample_type(self, sample_request):
        try:
            sample_type = sample_request.getSampleType()
            return sample_type.Title()
        except:
            return ''

    def get_strain(self, sample_request):
        try:
            strain = sample_request.getField('Strain').get(sample_request)
            return strain.Title()
        except:
            return ''

class CollectionRequestEdit(BrowserView):
    template = ViewPageTemplateFile('templates/collectionrequest_edit.pt')

    def __call__(self):
        # portal = self.portal
        request = self.request
        context = self.context
        # setup = portal.bika_setup

        if 'submitted' in request:

            context.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)

            # self.perform_sample_shipment_audit(self.context, request)
            context.getField('description').set(context, self.request.form['description'])
            context.getField('DateCreated').set(context, self.request.form['DateCreated'])
            # context.getField('SelectedSample').set(context, self.request.form['SelectedSample'])
            context.getField('Technician').set(context, self.request.form['Technician'])
            context.getField('Technique').set(context, self.request.form['Technique'])
            # context.getField('PersonPooling').set(context, self.request.form['PersonPooling'])
            context.reindexObject()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        return self.template()

    def perform_sample_shipment_audit(self, sample_shipment, request):
        audit_logger = AuditLogger(self.context, 'SampleShipment')
        pc = getToolByName(self.context, "portal_catalog")

        audit_logger.perform_multi_reference_audit(sample_shipment, 'SamplesList',
                                                                sample_shipment.getField('SamplesList').get(sample_shipment),
                                                                pc, request.form['SamplesList_uid'])

        if sample_shipment.getField('FromEmailAddress').get(sample_shipment) != request.form['FromEmailAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'FromEmailAddress', sample_shipment.getField('FromEmailAddress').get(sample_shipment),
                                              request.form['FromEmailAddress'])

        if sample_shipment.getField('ToEmailAddress').get(sample_shipment) != request.form['ToEmailAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'ToEmailAddress', sample_shipment.getField('ToEmailAddress').get(sample_shipment),
                                              request.form['ToEmailAddress'])

        audit_logger.perform_reference_audit(sample_shipment, 'Client', sample_shipment.getField('Client').get(sample_shipment),
                                             pc, request.form['Client_uid'])

        if sample_shipment.getField('DeliveryAddress').get(sample_shipment) != request.form['DeliveryAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'DeliveryAddress', sample_shipment.getField('DeliveryAddress').get(sample_shipment),
                                              request.form['DeliveryAddress'])

        if sample_shipment.getField('BillingAddress').get(sample_shipment) != request.form['BillingAddress']:
            audit_logger.perform_simple_audit(sample_shipment, 'BillingAddress', sample_shipment.getField('BillingAddress').get(sample_shipment),
                                              request.form['BillingAddress'])

        # shipping date audit
        form_shipping_date = request.form['ShippingDate']
        if form_shipping_date:
            form_shipping_date = DateTime(getLocalServerTime(form_shipping_date))
        object_shipping_date = sample_shipment.getField('ShippingDate').get(sample_shipment)
        if not object_shipping_date:
            object_shipping_date = ''
        if object_shipping_date != form_shipping_date:
            audit_logger.perform_simple_audit(sample_shipment, 'ShippingDate', object_shipping_date, form_shipping_date)

        # date dispatched audit
        date_dispatched = request.form['DateDispatched']
        if date_dispatched:
            date_dispatched = DateTime(getLocalServerTime(date_dispatched))
        object_date_dispatched = sample_shipment.getField('DateDispatched').get(sample_shipment)
        if not object_date_dispatched:
            object_date_dispatched = ''
        if object_date_dispatched != date_dispatched:
            audit_logger.perform_simple_audit(sample_shipment, 'DateDispatched',
                                              object_date_dispatched, date_dispatched)

        # date delivered audit
        date_delivered = request.form['DateDelivered']
        if date_delivered:
            date_delivered = DateTime(getLocalServerTime(date_delivered))
        object_date_delivered = sample_shipment.getField('DateDelivered').get(sample_shipment)
        if not object_date_delivered:
            object_date_delivered = ''
        if object_date_delivered != date_delivered:
            audit_logger.perform_simple_audit(sample_shipment, 'DateDelivered',
                                              object_date_delivered, date_delivered)

        if sample_shipment.getField('Courier').get(sample_shipment) != request.form['Courier']:
            audit_logger.perform_simple_audit(sample_shipment, 'Courier', sample_shipment.getField('Courier').get(sample_shipment),
                                              request.form['Courier'])

        if sample_shipment.getField('CourierInstructions').get(sample_shipment) != request.form['CourierInstructions']:
            audit_logger.perform_simple_audit(sample_shipment, 'CourierInstructions', sample_shipment.getField('CourierInstructions').get(sample_shipment),
                                              request.form['CourierInstructions'])

        if sample_shipment.getField('TrackingURL').get(sample_shipment) != request.form['TrackingURL']:
            audit_logger.perform_simple_audit(sample_shipment, 'TrackingURL', sample_shipment.getField('TrackingURL').get(sample_shipment),
                                              request.form['TrackingURL'])

        # Shipment condition audit
        if sample_shipment.getField('ShipmentConditions').get(sample_shipment) != request.form['ShipmentConditions']:
            audit_logger.perform_simple_audit(sample_shipment, 'ShipmentConditions', sample_shipment.getField('ShipmentConditions').get(sample_shipment),
                                              request.form['ShipmentConditions'])

        # Shipping costs audit
        form_shipping_cost = request.form['ShippingCost']
        if not form_shipping_cost:
            form_shipping_cost = 0
        else:
            form_shipping_cost = float(form_shipping_cost)

        object_shipping_cost = sample_shipment.getField('ShippingCost').get(sample_shipment)
        if not object_shipping_cost:
            object_shipping_cost = 0
        else:
            object_shipping_cost = float(object_shipping_cost)

        if form_shipping_cost != object_shipping_cost:
            audit_logger.perform_simple_audit(sample_shipment, 'ShippingCost', object_shipping_cost,
                                              form_shipping_cost)

        # The weight audit
        form_weight = request.form['Weight']
        if not form_weight:
            form_weight = 0
        else:
            form_weight = float(form_weight)

        object_weight = sample_shipment.getField('Weight').get(sample_shipment)
        if not object_weight:
            object_weight = 0
        else:
            object_weight = float(object_weight)

        if object_weight != form_weight:
            audit_logger.perform_simple_audit(sample_shipment, 'Weight', object_weight, form_weight)

        if sample_shipment.getField('Volume').get(sample_shipment) != request.form['Volume']:
            audit_logger.perform_simple_audit(sample_shipment, 'Volume', sample_shipment.getField('Volume').get(sample_shipment),
                                              request.form['Volume'])

    # def get_fields_with_visibility(self, visibility, mode=None):
    #     mode = mode if mode else 'edit'
    #     schema = self.context.Schema()
    #     fields = []
    #     for field in schema.fields():
    #         isVisible = field.widget.isVisible
    #         v = isVisible(self.context, mode, default='invisible', field=field)
    #         accepted_fields = ['title', 'description', 'DateCreated', 'Technician', 'Technique']
    #         if v == visibility and field.getName() in accepted_fields:
    #             fields.append(field)
    #     return fields

    def prepare_human_sample_request_rows(self):

        human_sample_request_rows = self.context.get_human_sample_requests()
        prepared_request_rows = []

        for sample_request in human_sample_request_rows:
            approved = sample_request.getField('Approved').get(sample_request)
            approval_status = self.get_approval_status(approved)

            prepared_request = {
                'UID': sample_request.UID(),
                'status_approved': approval_status['approved_status'],
                'status_rejected': approval_status['rejected_status'],
                'status_unspecified': approval_status['unspecified_status'],
                'barcode': sample_request.getField('Barcode').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'volume': sample_request.getField('Volume').get(sample_request),
                'unit': sample_request.getField('Unit').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)


        print('==============The human sample requests')
        print(prepared_request_rows)
        return prepared_request_rows

    def prepare_microbe_sample_request_rows(self):

        microbe_sample_request_rows = self.context.get_microbe_sample_requests()
        prepared_request_rows = []

        for sample_request in microbe_sample_request_rows:
            approved = sample_request.getField('Approved').get(sample_request)
            approval_status = self.get_approval_status(approved)

            prepared_request = {
                'UID': sample_request.UID(),
                'status_approved': approval_status['approved_status'],
                'status_rejected': approval_status['rejected_status'],
                'status_unspecified': approval_status['unspecified_status'],
                'identification': sample_request.getField('Identification').get(sample_request),
                'strain': self.get_strain(sample_request),
                'origin': sample_request.getField('Origin').get(sample_request),
                'sample_type': self.get_sample_type(sample_request),
                'phenotype': sample_request.getField('Phenotype').get(sample_request),
            }
            prepared_request_rows.append(prepared_request)

        return prepared_request_rows

    def get_approval_status(self, approval):
        approval_status = {
            'rejected_status': False,
            'approved_status': False,
            'unspecified_status': False,
        }

        if approval == 'rejected':
            approval_status['rejected_status'] = True
            return approval_status

        if approval == 'approved':
            approval_status['approved_status'] = True
            return approval_status

        approval_status['unspecified_status'] = True
        return approval_status

    def get_client(self, collection_request):
        try:
            client = collection_request.getField('Client').get(collection_request)
            return client.Title()
        except:
            return ''

    def get_sample_kingdom(self, collection_request):
        try:
            sample_kingdom = collection_request.getSampleKingdom()
            return sample_kingdom.Title()
        except:
            return ''


    def get_sample_type(self, sample_request):
        try:
            sample_type = sample_request.getSampleType()
            return sample_type.Title()
        except:
            return ''

    def get_strain(self, sample_request):
        try:
            strain = sample_request.getField('Strain').get(sample_request)
            return strain.Title()
        except:
            return ''

    def get_fields_with_visibility(self, visibility, schemata, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():

            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:

                if field.schemata == schemata:
                    fields.append(field)

        return fields

class GetCentrifugationData(BrowserView):

    def __init__(self, context, request):

        super(GetCentrifugationData, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        uc = getToolByName(self.context, 'portal_catalog')

        try:
            uid = self.request['UID']
            brains = uc.searchResults(portal_type='Centrifugation', UID=uid)
            sample_pooling = brains[0].getObject()

            return_val = {
                'date_created': str(sample_pooling.getField('DateCreated').get(sample_pooling) or ''),
            }

            return json.dumps(return_val)

        except:
            return json.dumps({
                'date_created': '',
            })


class ajaxGetProjects(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetProjects, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # plone.protect.CheckAuthenticator(self.request)

        rows = []

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Project")

        for project in brains:
            rows.append({
                project.UID: project.Title
            })

        return json.dumps(rows)


class ajaxGetSampleTypes(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        super(ajaxGetSampleTypes, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        # plone.protect.CheckAuthenticator(self.request)
        rows = []

        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="SampleType")

        for sample_type in brains:
            rows.append({
                sample_type.UID: sample_type.Title
            })

        return json.dumps(rows)
