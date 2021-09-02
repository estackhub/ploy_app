import frappe
from frappe.utils.data import add_days, today, add_months
import json
import os

def before_install():
  
  # Fetching user list
  filters = {
    'enabled': 1,
    'name': ['not in',['Guest', 'Administrator']]
  }
  
  user_list = frappe.get_list('User', filters = filters, fields = ["name"])

  active_users = 0

  for user in user_list:
    roles = frappe.get_list("Has Role", filters = {
      'parent': user.name
    }, fields = ['role'])
    for row in roles:
      if frappe.get_value("Role", row.role, "desk_access") == 1: 
        active_users += 1
        break
  
  trials =  add_days(today(), 30) 
  

  data = {
    'users': 2,
    'active_users': active_users,
    'space': 1280,
    'db_space': 100,
    'company': 1,
    'used_company': 1,
    'count_website_users': 0,
    'count_administrator_user': 0,
    'valid_till': trials,
    'status': 'freemium',
    'trial_ends': trials,
    'warehouse': 2,
    'used_warehouse': 1,
    'loan':trials,
    'payroll': trials,
    'hr': trials,
    'crm': trials,
    'project': trials,
    'care': trials
  }
  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(data, outfile, indent= 2)

  file_path = frappe.utils.get_bench_path() + '/' + \
    frappe.utils.get_site_name(frappe.local.site) + \
      '/allot.json'
  
  print('\nfile allot.json created at ', file_path, 'with the following settings:')
  for key in data: print("\t{}: {}".format(key, data[key]))
  print('\nChange the values in allot.json to change limits\n')