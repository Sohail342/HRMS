from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Branch, Region, FunctionalGroup, Group

class BranchResource(resources.ModelResource):
    # Map the 'branch_region' to use the 'name' field of Region
    branch_region = fields.Field(
        column_name='branch_region',  # CSV column name
        attribute='branch_region',   # Model field
        widget=ForeignKeyWidget(Region, 'name')  # Match using Region's 'name' field
    )

    class Meta:
        model = Branch
        fields = ('branch_code', 'branch_name', 'branch_Category', 'branch_address', 'branch_region')  # Fields to import/export
        import_id_fields = ('branch_code',)  # Unique field for identifying rows during import


class FunctionalGroupResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='name')  # Referencing the Group model's name field
    )

    class Meta:
        model = FunctionalGroup
        fields = ('id', 'name', 'allias', 'group')  # Fields to include in import/export
        export_order = ('id', 'name', 'allias', 'group')  # Order of fields in the exported file


class RegionResource(resources.ModelResource):
    functional_group = fields.Field(
        column_name='functional_group',
        attribute='functional_group',
        widget=ManyToManyWidget(FunctionalGroup, separator=',', field='name')  # Handles ManyToManyField using 'name'
    )

    class Meta:
        model = Region
        fields = ('id', 'name', 'region_category', 'functional_group')  # Fields to include
        export_order = ('id', 'name', 'region_category', 'functional_group')  # Export field order
