from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from . import util
import markdown2
from django.core.files.storage import default_storage
import random
from django.urls import reverse

# Create your views here.

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    entry= util.get_entry(title)
    if entry is None:
        return render(request, 'encyclopedia/notfound.html', {
            "title": title,
            "form": SearchForm()
        })
    else:
        return render(request, 'encyclopedia/entry.html', {
            "title": title,
            "entry": markdown2.markdown(entry),
            "entry_row": entry,
            "form": SearchForm()
        })    

# Serach form
class SearchForm(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Wiki'}))
# New entry form
class NewPageForm(forms.Form):
    title = forms.CharField(label="title", widget=forms.TextInput(attrs={'id': 'new-entry-title'}))
    data = forms.CharField(label="data", widget=forms.TextInput(attrs={'id': 'edit-entry'}))
# Edit form for entry
class EditForm(forms.Form):
    title = forms.CharField(label="title", widget=forms.TextInput(attrs={'id': 'edit-entry-title'}))
    data = forms.CharField(label="data", widget=forms.TextInput(attrs={'id': "edit-entry"}))


   
def search(request):
    form = SearchForm()
    is_substring_of_queries = []
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            for entry in util.list_entries():
                existsIdenticalResult = form.cleaned_data["query"].casefold() == entry.casefold() 
                existsResult = form.cleaned_data["query"].casefold() in entry.casefold()    
                if existsIdenticalResult:
                    return HttpResponseRedirect(reverse("wiki",
                     kwargs={"page_title": entry}))
                elif existsResult: 
                    is_substring_of_queries.append(entry)      
    context = {
        "form": SearchForm(),
        "is_substring_of_queries": is_substring_of_queries
    }

    response = render(request, "encyclopedia/search.html", context)
    return response


def create(request):
    if request.method == "POST":
        # Requesting Form for new entry
        new_entry = NewPageForm(request.POST)
        if new_entry.is_valid():
            title = new_entry.cleaned_data["title"]
            data = new_entry.cleaned_data["data"]
            entries_all = util.list_entries()
            for entry in entries_all:
                if entry.lower() == title.lower():
                    return render(request, 'encyclopedia/create.html', {
                        "form": SearchForm(),
                        "newpageform": NewPageForm(),
                        "error": "The Entry already Exists"
                    })
            # Markdown for content entry
            new_entry_title="#" + title 
            # New line to seperate title from content
            new_entry_data="\n" + data 
            # Combine Content Entry and Entry title
            new_entry_content= new_entry_title + new_entry_data 
            # Save new entry
            util.save_entry(title, new_entry_content)
            entry= util.get_entry(title)
            # Render page
            return render(request, 'encyclopedia/create.html', {
                "title": title,
                "entry": markdown2.markdown(title),
                "form": SearchForm()
            })      
    return render(request, 'encyclopedia/create.html', {
        "form": SearchForm(),
        "newpageform": NewPageForm()
    })

def edit(request):
    if request.method == "POST":
        # Get data for entry
        entry= util.get_entry(title)
        # Display Content for entry to be edited
        edit_form= EditForm()
        if edit_form.is_valid():
            title = form.cleaned_data["title"]
            data = form.cleaned_data["data"]
            entries_all = util.list_entries()
            for entry in entries_all:
                if entry.lower() == title.lower():
                  return render(request, 'encyclopedia/edit.html', {
                      "form": SearchForm(),
                      "editform": EditForm(),
                      "error": f"Entry still the Same!!!"
                  })
            # Markdown for content entry
            edited_entry_title="#" + title 
            # New line to seperate title from content
            edited_entry_data="\n" + data 
            # Combine Content Entry and Entry title
            edited_entry_content= edited_entry_title + edited_entry_data 
            # Save edited entry
            util.save_entry(title, edited_entry_content)
            entry= util.get_entry(title)    
        # Render page with information
        return render(request, 'encyclopedia/edit.html', {
            "form": SearchForm(),
            "editform": edit_form,
            "entry": entry,
            "title": title
        })
    return render(request, 'encyclopedia/edit.html', {
        "form": SearchForm(),
        "edit": EditForm()
    })    


def submit(request, title):
    if request.method == "POST":
        # Extract Entry Information
        edit_entry=EditForm(request.POST)
        if edit_entry.is_valid():
            # Extract data from entry
            content= edit_entry.cleaned_data["data"]
            # Extract title from entry
            title_edit= edit_entry.cleaned_data["title"]
            # if title edited delete old data
            if title_edit != title:
                filename= f"entries/{ title }.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)
            # Sve new data
            util.save_entry(title_edit, content)
            # Get new entry
            entry= util.get_entry(title_edit)
            msg_success= "Successfully Updated"        
        # Render page with new data
        return render(request, 'encyclopedia/entry.html', {
            "title": title_edit,
            "entry": markdown2.markdown(entry),
            "form": SearchForm(),
            "msg_success": msg_success
        })

def random(request):
    # List all entries
    entries = util.list_entries()
    # Tilte of Random selected entry
    title = random(entries)
    # Content of selected entry
    entry= util.get_entry(title)
    # Render page
    return HttpResponseRedirect(reverse("entry", args=[title]))



