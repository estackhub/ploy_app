import frappe
from frappe.utils.data import today, date_diff, add_days
import json
import subprocess
import datetime
from frappe.utils import cint
from frappe import _

def user_limit(self, method):
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      parsed = json.load(jsonfile)
  count_website_users = parsed["count_website_users"]
  count_administrator_user = parsed["count_administrator_user"]
  allowed_users = parsed["users"]

  active_users = validate_users(self, count_administrator_user, count_website_users, allowed_users)   

  data = {}
  with open(frappe.get_site_path('allot.json')) as outfile:
    data = json.load(outfile)
  data['active_users'] = active_users

  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(data, outfile, indent= 2)


def files_space_limit(self, method):
  validate_files_space_limit()


def validate_files_space_limit():
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      parsed = json.load(jsonfile)
  allowed_space = parsed["space"]

  site_path = frappe.get_site_path()
  private_files_path = site_path + '/private/files'
  public_files_path  = site_path + '/public/files'
  backup_files_path = site_path + '/private/backups'

  # Calculating Sizes
  total_size = get_directory_size(site_path)
  private_files_size = get_directory_size(private_files_path)
  public_files_size = get_directory_size(public_files_path)
  backup_files_size = get_directory_size(backup_files_path)
  
  parsed['used_space'] = total_size
  parsed['private_files_size'] = private_files_size
  parsed['public_files_size'] = public_files_size
  parsed['backup_files_size'] = backup_files_size

  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

  var_type = type(allowed_space)
  
  if var_type == str and allowed_space == 'Unlimited': pass

  #added by me
  elif var_type == int and total_size < allowed_space: pass
  
  elif var_type == int and total_size > allowed_space:
      msg = '<div>You have exceeded your files space limit. Delete some files from file manager or to incease the limit please contact sales</div>'
      msg += '<div><ul><li>Private Files: {}MB</li><li>Public Files: {}MB</li><li>Backup Files: {}MB</li></ul></div>'.format(private_files_size, public_files_size, backup_files_size)
      frappe.throw(_(msg))
  else:
    frappe.throw(_("Invalid value. Can be 'Unlimited' or an Integer"), frappe.ValidationError)


def db_space_limit(self, method):
  validate_db_space_limit()

def validate_db_space_limit():
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      parsed = json.load(jsonfile)
  allowed_db_space = parsed["db_space"]
  used_db_space = frappe.db.sql('''SELECT `table_schema` as `database_name`, SUM(`data_length` + `index_length`) / 1024 / 1024 AS `database_size` FROM information_schema.tables  GROUP BY `table_schema`''')[1][1]
  used_db_space = int(used_db_space)
  parsed['used_db_space'] = used_db_space
  
  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(parsed, outfile, indent= 2)

  var_type = type(allowed_db_space)
  
  if var_type == str and allowed_db_space == 'Unlimited': pass

  #added by me
  elif var_type == int and used_db_space < allowed_db_space: pass
  
  elif var_type == int and used_db_space > allowed_db_space:
      msg = '<div>You have exceeded your Database Size Limit. Please contact sales to upgrade your package</div>'
      msg += '<ul><li>Allowed Space: {}MB</li><li>Used Space: {}MB</li></ul>'.format(allowed_db_space, used_db_space)
      frappe.throw(_(msg))
  else:
    frappe.throw(_("Invalid value. Can be 'Unlimited' or an Integer"), frappe.ValidationError)


def company_limit(self,method):
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      limit_setting = json.load(jsonfile)

  total_company = len(frappe.db.get_all('Company',filters={}))
  allowed_companies = limit_setting.get('company')
  
  var_type = type(allowed_companies)
  
  if var_type == str and allowed_companies == 'Unlimited': pass

  #added by me
  elif var_type == int and total_company <= allowed_companies: pass
  
  elif var_type == int and total_company >= allowed_companies:
      if not frappe.get_list('Company', filters={
        'name': self.name
      }):  
        frappe.throw(_("Only {} company(s) allowed and you have {} company(s).Please remove other company or to increase the limit please contact sales").format(limit_setting.get('company'),total_company))
  
  else:
    frappe.throw(_("Invalid value. Can be 'Unlimited' or an Integer"), frappe.ValidationError)

  with open(frappe.get_site_path('allot.json')) as outfile:
    data = json.load(outfile)
    data['used_company'] = total_company
  with open(frappe.get_site_path('allot.json'), 'w') as outfile:
    json.dump(data, outfile, indent= 2)


def validate_users(self, count_administrator_user, count_website_users, allowed_users):
  '''
  validates and returns active users
  '''
  # Fetching user list
  filters = {}
  if count_administrator_user == 0:
    filters = {
    'enabled': 1,
    'name': ['not in',['Guest', 'Administrator']]
  }
  else:
    filters = {
    'enabled': 1,
    'name': ['!=','Guest']
  }
  user_list = frappe.get_list('User', filters = filters, fields = ["name"])

  active_users = 0
  # Validating if website users are to be counted or not
  if count_website_users == 1 : active_users = len(user_list)
  else:
    for user in user_list:
      if user.name == 'Administrator' and count_administrator_user == 0:
        continue

      roles = frappe.get_list("Has Role", filters = {
        'parent': user.name
      }, fields = ['role'])
      for row in roles:
        if frappe.get_value("Role", row.role, "desk_access") == 1: 
          active_users += 1
          break

  var_type = type(allowed_users)
  
  if var_type == str and allowed_users == 'Unlimited': pass
  
  #add by me
  elif var_type == int and active_users <= allowed_users: pass
  #i modify from '>=' to >
  elif var_type == int and active_users >= allowed_users:
      if not frappe.get_list('User', filters={
        'name': self.name
      }):
        frappe.throw('Only {} active users allowed and you have {} active users. Please disable users or to increase the limit please contact sales'. format(allowed_users, len(user_list))) 
      elif self.enabled == 1 and active_users > allowed_users:
        frappe.throw('Only {} active users allowed and you have {} active users. Please disable users or to increase the limit please contact sales'. format(allowed_users, len(user_list)-1))
  else:
    frappe.throw(_("Invalid value. Can be 'Unlimited' or an Integer"), frappe.ValidationError)

  return active_users

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

def validate_freemium():
  '''
  returns status
  '''
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      parsed = json.load(jsonfile)
  trial = parsed["trial_ends"]
  status = parsed["status"]
  loan_app = parsed["loan_app"]
  payroll = parsed["payroll"]
  hr_app = parsed["hr_app"]
  trial_end = datetime.datetime.fromtimestamp(
    trial).strftime('%Y-%m-%d %H:%M:%S')
  #datetime.datetime.now().date()

def validate_freemium_limit (self, module):
  """ work on to get limit """
  with open(frappe.get_site_path('allot.json')) as jsonfile:
      parsed = json.load(jsonfile)
  trial_period = parsed["trial_ends"]
  module_status = parsed[module]
  # trial_end = datetime.datetime.fromtimestamp(trial_period).strftime(
  #   '%Y-%m-%d %H:%M:%S')
  diff = date_diff(trial_period, today())
  if diff > 0 and module_status == 'close' : pass 
  elif diff < 0 and module_status == 'active': pass
  elif diff < 0 and module_status == 'close':
    msg = '<div> You have exceeded Limit. Please contact Support to upgrade your package</div>'
    frappe.throw(_(msg))
  else:
    frappe.throw(_("Invalid access. Cant be 'Unlimited' "), frappe.ValidationError)
  

def loan_status(self, method):
  """ getting set """
  validate_freemium_limit(self, 'loan_app')

def payroll_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'payroll')

def hrm_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'hr_app')

def project_status(self, method):
  ''' '''
  validate_freemium_limit(self, 'projects_app')
