import frappe
import json
import subprocess
from frappe import _

# User
def user_limit(self, method):
  # JSON file path
  json_file_path = frappe.get_site_path('allot.json')
  
  # Reading File
  with open(json_file_path) as jsonfile: 
    parsed = json.load(jsonfile)
  
  count_website_users = parsed["count_website_users"]
  count_administrator_user = parsed["count_administrator_user"]
  allowed_users = parsed["users"]

  active_users = validate_users(self, count_administrator_user, count_website_users, allowed_users)   

  # Writing File
  parsed['active_users'] = active_users
  with open(json_file_path, 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

def validate_users(self, count_administrator_user, count_website_users, allowed_users):
  
  # allowed user value type check
  if type(allowed_users) is not int:
    frappe.throw(_("Invalid value for maximum User Allowed limit. it can be a whole number only."), frappe.ValidationError)

  # Fetching all active users list
  filters = {
    'enabled': 1,
    "name": ['!=','Guest'] 
  }

  # if we don't have to count administrator also
  if count_administrator_user == 0:
    filters['name'] = ['not in',['Guest', 'Administrator']]

  user_list = frappe.get_list('User', filters, ["name"])
  active_users = len(user_list)
  is_desk = ""

  # if don't have to count website users
  if not count_website_users:
    active_users = 0
    is_desk = "Desk"

    for user in user_list:
      roles = frappe.get_list("Has Role", { 'parent': user.name}, ['role'])
      for row in roles:
        if frappe.get_value("Role", row.role, "desk_access") == 1: 
          active_users += 1
          break

  # Users limit validation
  if allowed_users != 0 and active_users >= allowed_users:
      if not frappe.get_list('User', filters={'name': self.name}):
        frappe.throw('Only {} active {} users allowed and you have {} active users. Please disable users or to increase the limit please contact support'. format(allowed_users, is_desk, active_users))

  return active_users

# Files
def files_space_limit(self, method):
  validate_files_space_limit()

def validate_files_space_limit():
  '''
  Validates files space limit
  '''

  # JSON file path
  json_file_path = frappe.get_site_path('allot.json')
  
  # Reading File
  with open(json_file_path) as jsonfile:
      parsed = json.load(jsonfile)
  
  allowed_space = parsed["space"]

  # allowed space value type check
  if type(allowed_space) is not int:
    frappe.throw(_("Invalid value for maximum Space limit. It can be a whole number only."), frappe.ValidationError)


  # all possible file locations
  site_path = frappe.get_site_path()
  private_files_path = site_path + '/private/files'
  public_files_path  = site_path + '/public/files'
  backup_files_path = site_path + '/private/backups'

  # Calculating Sizes
  total_size = get_directory_size(site_path)
  private_files_size = get_directory_size(private_files_path)
  public_files_size = get_directory_size(public_files_path)
  backup_files_size = get_directory_size(backup_files_path)
  
  
  # Writing File
  parsed['used_space'] = total_size
  parsed['private_files_size'] = private_files_size
  parsed['public_files_size'] = public_files_size
  parsed['backup_files_size'] = backup_files_size

  with open(json_file_path, 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

  
  if allowed_space != 0 and total_size > allowed_space:
    msg = '<div>You have exceeded your files space limit. Delete some files from file manager or to increase the limit please contact support</div>'
    msg += '<div><ul><li>Private Files: {}MB</li><li>Public Files: {}MB</li><li>Backup Files: {}MB</li></ul></div>'.format(private_files_size, public_files_size, backup_files_size)
    frappe.throw(_(msg))

# DB
def db_space_limit(self, method):
  validate_db_space_limit()

def validate_db_space_limit():
  '''
  Validates DB space limit
  '''

  # JSON file path
  json_file_path = frappe.get_site_path('allot.json')
  
  # Reading File
  with open(json_file_path) as jsonfile:
      parsed = json.load(jsonfile)
  
  allowed_db_space = parsed["db_space"]
  
  # allowed DB space value type check
  if type(allowed_db_space) is not int:
    frappe.throw(_("Invalid value for maximum Database Space limit. it can be a whole number only."), frappe.ValidationError)

  # Getting DB Space
  used_db_space = frappe.db.sql('''SELECT `table_schema` as `database_name`, SUM(`data_length` + `index_length`) / 1024 / 1024 AS `database_size` FROM information_schema.tables  GROUP BY `table_schema`''')[1][1]
  used_db_space = int(used_db_space)
  
  # Writing File
  parsed['used_db_space'] = used_db_space
  
  with open(json_file_path, 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

  if allowed_db_space != 0 and used_db_space > allowed_db_space:
      msg = '<div>You have exceeded your Database Size limit. Please contact support to upgrade your package</div>'
      msg += '<ul><li>Allowed Space: {}MB</li><li>Used Space: {}MB</li></ul>'.format(allowed_db_space, used_db_space)
      frappe.throw(_(msg))

# Company    
def company_limit(self, method):
  '''
  Validates Company limit
  '''
  
  # JSON file path
  json_file_path = frappe.get_site_path('allot.json')
  
  # Reading File
  with open(json_file_path) as jsonfile:
      parsed = json.load(jsonfile)

  allowed_companies = parsed.get('company')
  
  # allowed Companies value type check
  if type(allowed_companies) is not int:
    frappe.throw(_("Invalid value for maximum allowed Companies limit. it can be a whole number only."), frappe.ValidationError)
  
  # Calculating total companies
  total_company = len(frappe.db.get_all('Company',filters={}))
  
  # Writing file
  parsed['used_company'] = total_company  
  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

  # Validation
  if allowed_companies != 0 and total_company >= allowed_companies:
      if not frappe.get_list('Company', {'name': self.name}):  
        frappe.throw(_("Only {} company(s) allowed and you have {} company(s).Please remove other company or to increase the limit please contact support").format(parsed.get('company'), total_company))

# Directory Size
def get_directory_size(path):
  '''
  returns total size of directory in MBss
  '''
  output_string = subprocess.check_output(["du","-mcs","{}".format(path)])
  total_size = ''
  for char in output_string:
    if chr(char) == "\t":
      break
    else:
      total_size += chr(char)
  
  return int(total_size)

# ##added modules

# Warehouse    
def warehouse_limit(self, method):
  '''
  Validates Warehouse limit
  '''
  
  # JSON file path
  json_file_path = frappe.get_site_path('allot.json')
  
  # Reading File
  with open(json_file_path) as jsonfile:
      parsed = json.load(jsonfile)

  allowed_warehouses = parsed.get('warehouse')
  
  # allowed Warehouses value type check
  if type(allowed_warehouses) is not int:
    frappe.throw(_("Invalid value for maximum allowed Warehouses limit. it can be a whole number only."), frappe.ValidationError)
  
  # Calculating total warehouses
  total_warehouse = len(frappe.db.get_all('Warehouse',filters={})) - 1
  
  # Writing file #candidate for remove
  parsed['used_warehouse'] = total_warehouse 
  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

  # Validation
  if allowed_warehouses != 0 and total_warehouse >= allowed_warehouses:
      if not frappe.get_list('Warehouse', {'name': self.name}):  
        frappe.throw(_("Only {} warehouse(s) allowed and you have {} warehouse(s).Please remove other warehouse or to increase the limit please contact support").format(parsed.get('warehouse'), total_warehouse))


def validate_freemium_limit (self, module):
  """ work on to get limit """
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      parsed = json.load(jsonfile)
  trial_period = parsed["trial_ends"]
  module_status = parsed[module]
  # trial_end = datetime.datetime.fromtimestamp(trial_period).strftime(
  #   '%Y-%m-%d %H:%M:%S')
  diff = date_diff(trial_period, today())
  dued = date_diff(module_status, today())
  if diff > 0  : pass 
  elif diff < 0 and dued > 0 : pass
  elif diff < 0 and dued < 0 :
    msg = '<div> You have exceeded Limit. Please contact Support to upgrade your package</div>'
    frappe.throw(_(msg))
  else:
    frappe.throw(_("Invalid access. 'Unlimited' not available "), frappe.ValidationError)
  

def loan_status(self, method):
  """ getting set """
  validate_freemium_limit(self, 'loan')

def payroll_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'payroll')

def hrm_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'hr')

def crm_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'crm')

def project_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'project')

def care_status(self, method):
  ''' '''
  validate_freemium_limit(self,'care')
  


