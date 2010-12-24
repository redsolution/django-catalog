# -*- codingL utf-8 -*-
from django import forms
from models import Link, TreeItem
from mptt.forms import TreeNodePositionField, TreeNodeChoiceField
from django.contrib.contenttypes.models import ContentType


class LinkInsertionForm(forms.models.ModelForm):
    '''
    Link adding and editing form, inserts link into catalog tree
    '''
    
    class Meta:
        model = Link

    treeitem = TreeNodeChoiceField(queryset=TreeItem.objects.all())
    position = TreeNodePositionField()
    # Just in case the user can not edit these fields directly
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(),
        widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())

    def save(self, *args, **kwds):
        instance = super(LinkInsertionForm, self).save(*args, **kwds) 
        new_tree_item = TreeItem(content_object=instance)
        
        target_tree_item = self.cleaned_data['treeitem']
        position = self.cleaned_data['position']
         
        return TreeItem.tree.insert_node(new_tree_item, target_tree_item,
            position, save=True)
