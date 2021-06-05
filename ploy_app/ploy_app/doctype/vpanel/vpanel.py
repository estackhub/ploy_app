# Copyright (c) 2021, Jide Olayinka and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from dateutil.parser import parse
from ploy_app.ploy_app.allot import validate_users
import frappe
from frappe.model.document import Document
import json
import subprocess

class VPanel(Document):
  @frappe.whitelist()
  def get_usage_info(self):
    usage = {}
    with open(frappe.get_site_path('allot.json')) as jsonfile:
        parsed = json.load(jsonfile)

    for key, value in parsed.items():
      usage[key] = value

    for key, value in usage.items():
      self.db_set(key, value)
