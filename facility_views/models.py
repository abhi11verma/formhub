from django.db import models
from facilities.models import *

class FacilityTable(models.Model):
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    
    @property
    def display_dict(self):
        variables = list(self.variables.all())
        column_variables = [v.display_dict for v in variables]
        return {
            'name': self.name,
            'slug': self.slug,
            'columns': column_variables,
            'subgroups': [{'name': s.name,
                'slug': s.slug} for s in self.subgroups.all()]
        }
    
    def add_variable(self, variable_data):
        variable_data['facility_table'] = self
        
        subgroup_list = variable_data.get('subgroups')
        if subgroup_list is not None:
            subgroups = subgroup_list.split(' ')
            for subgroup in subgroups:
                if subgroup is not '':
                    col, created = ColumnCategory.objects. \
                        get_or_create(name=subgroup, slug=subgroup, table=self)
        TableColumn.objects.get_or_create(**variable_data)

class TableColumn(models.Model):
    #there's a lot of overlap with facilities.Variable, but there's view-specific stuff
    #that needs a home.
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    description = models.CharField(max_length=255, null=True)
    clickable = models.BooleanField(default=False)
    subgroups = models.CharField(max_length=512, null=True)
    variable_id = models.IntegerField(null=True)
    
    facility_table = models.ForeignKey(FacilityTable, related_name="variables")
    
    @property
    def display_dict(self):
        d = {
            'name': self.name,
            'slug': self.slug,
            'subgroups': self.subgroups.split(' '),
            'clickable': self.clickable
        }
        if not self.description in [None, '']:
            d['description'] = self.description
        return d

class ColumnCategory(models.Model):
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    table = models.ForeignKey(FacilityTable, related_name='subgroups')