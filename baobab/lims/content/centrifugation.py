from Products.Archetypes.references import HoldingReference
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from zope.interface import implements
from Products.CMFCore import permissions

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import DateTimeWidget

from baobab.lims.config import PROJECTNAME
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import ICentrifugation

from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName

SelectedSample = ReferenceField(
    'SelectedSample',
    allowed_types=('Sample'),
    referenceClass=HoldingReference,
    relationship='CentrifugationSelectedSample',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Selected sample"),
        description=_("The selected sample"),
        size=40,
        base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_catalog',
        showOn=True
    )
)

DateCreation = DateTimeField(
    'DateCreated',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Created"),
        description=_("Define when the centrifugation has been created."),
        show_time=True,
        visible={'edit': 'visible', 'view': 'visible'}
    )
)

Technician = ReferenceField(
    'Technician',
    allowed_types=('LabContact'),
    referenceClass=HoldingReference,
    relationship='CentrifugationLabContact',
    mode="rw",
    widget=bika_ReferenceWidget(
        label=_("Technician"),
        description=_("The technician doing centrifugation."),
        size=40,
        # base_query={'review_state': 'sample_received', 'cancellation_state': 'active'},
        visible={'edit': 'visible', 'view': 'visible'},
        # catalog_name='bika_catalog',
        showOn=True
    )
)

#
# ReferenceField(
#         'LabContacts',
#         multiValued=1,
#         allowed_types=('LabContact'),
#         referenceClass=HoldingReference,
#         relationship='ProjectLabContact',
#         mode="rw",
#         widget=bika_ReferenceWidget(
#             label=_("Lab Contacts"),
#             # description=_("Lab Contacts"),
#             showOn=True
#         )
#     ),
#


Technique = StringField(
    'Technique',
    widget=StringWidget(
        label=_('Technique'),
        description=_('The technique used to centrifuged.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

Centrifuges = StringField(
    'Centrifuges',
    schemata='Centrifugations',
    widget=StringWidget(
        label=_('Centrifuges'),
        description=_('The technique used to centrifuged.'),
        visible={'view': 'visible', 'edit': 'visible'}
    )
)

schema = BikaSchema.copy() + Schema((
    SelectedSample,
    DateCreation,
    Technician,
    Technique,
    Centrifuges,
))

schema['title'].widget.visible = {'view': 'visible', 'edit': 'visible'}
schema['description'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class Centrifugation(BaseContent):
    implements(ICentrifugation)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # def getSelectedSample(self):
    #     selected_sample = self.getField('SelectedSample').get(self)
    #     if selected_sample:
    #         return selected_sample.Title()
    #     return ''
    #
    # def getTechnician(self):
    #     technician = self.getField('Technician').get(self)
    #     if technician:
    #         return technician.Title()
    #     return ''

    def get_selected_sample(self):
        selected_sample = self.getField('SelectedSample').get(self)
        if selected_sample:
            return selected_sample.Title()
        return ''

    def get_technician(self):
        technician = self.getField('Technician').get(self)
        if technician:
            return technician.Title()
        return ''

    def get_centrifugation_rows(self):
        centrifuges = self.getCentrifuges()

        samples = []
        for sample in centrifuges:
            samples.append(sample)

        return samples

registerType(Centrifugation, PROJECTNAME)
