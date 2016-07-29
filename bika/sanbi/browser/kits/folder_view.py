from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.sanbi import bikaMessageFactory as _
from bika.sanbi.permissions import *


class KitsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(KitsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Kit',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Kits"))
        self.icon = self.portal_url + \
                    "/++resource++bika.sanbi.images/kit_big.png"
        self.description = ""
        self.catalog = "bika_catalog"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'Prefix': {'title': _('Kit ID'),
                       'index': 'sortable_title',
                       'toggle': True},
            'kitTemplate': {'title': _('Kit template'),
                            'toggle': True},
            'quantity': {'title': _('Quantity'),
                         'toggle': True},
            'expiryDate': {'title': _('Expiry Date'),
                           'toggle': False},
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': ['Prefix', 'kitTemplate', 'quantity', 'expiryDate']
            },
            {
                'id': 'pending',
                'title': _('Pending'),
                'contentFilter': {'review_state': 'pending'},
                # 'transitions': [{'id':'complete'}, ],
                'columns': ['Prefix', 'kitTemplate', 'quantity', 'expiryDate']
            },
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddKit, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Kit',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageKits, self.context):
            # self.review_states[0]['transitions'].append({'id':'deactivate'})
            self.review_states.append(
                {
                    'id': 'completed',
                    'title': _('Completed'),
                    'contentFilter': {'review_state': 'completed'},
                    # 'transitions': [{'id':'store'}, ],
                    'columns': ['Prefix', 'kitTemplate', 'quantity',
                                'expiryDate']
                })
            self.review_states.append(
                {
                    'id': 'stored',
                    'title': _('Stored'),
                    'contentFilter': {'review_state': 'stored'},
                    # 'transitions': '',
                    'columns': ['Prefix', 'kitTemplate', 'quantity',
                                'expiryDate']
                })
            # self.review_states.append() # remove it
            stat = self.request.get("%s_review_state" % self.form_id, 'default')
            self.show_select_column = stat != 'all'
        return super(KitsView, self).__call__()

    def folderitems(self):
        items = super(KitsView, self).folderitems()
        # print items
        # print '-----'
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['kitTemplate'] = obj.getKitTemplateTitle()
            items[x]['replace']['Prefix'] = "<a href='%s'>%s</a>" % \
                                            (items[x]['url'], obj.getKitId())

        return items
