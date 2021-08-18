from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "ploy_app"
app_title = "Ploy App"
app_publisher = "Thrifty Digital"
app_description = "System usage listing and resources"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "spryng.managed@gmail.com"
app_license = "MIT"
#app_logo_url = '/assets/ploy_app/images/whitelabel_logo.jpg'

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/ploy_app/css/whitelabel_app.css"
app_include_js = "/assets/ploy_app/js/whitelabel.js"

# include js, css files in header of web template
web_include_css = "/assets/ploy_app/css/whitelabel_web.css"
# web_include_js = "/assets/ploy_app/js/ploy_app.js"


# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ploy_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }
'''
website_context = {
	"favicon": "/assets/ploy_app/images/whitelabel_logo.jpg",
	"splash_image": "/assets/ploy_app/images/whitelabel_logo.jpg"
}'''
after_migrate = ['ploy_app.api.whitelabel_patch']

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

before_install = "ploy_app.install.before_install"
# after_install = "ploy_app.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ploy_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
on_login = 'ploy_app.events.auth.successful_login'

doc_events = {
  'User': {
    'validate': 'ploy_app.ploy_app.allot.user_limit',
    'on_update': 'ploy_app.ploy_app.allot.user_limit'
	},
  'Company': {
    'validate':'ploy_app.ploy_app.allot.company_limit',
    'on_update':'ploy_app.ploy_app.allot.company_limit'
	},
  ('Stock Entry', 'Purchase Invoice', 'Payment', 'Journal Entry'):{
	  'on_submit' :'ploy_app.ploy_app.allot.db_space_limit'
	  },
  'File': {
    'validate': 'ploy_app.ploy_app.allot.files_space_limit'
	},
  ('Attendance','Expense Claim', 'Attendance Request', 'Employee Checkin','Leave Application', 'Shift Request', 'Shift Assignment', 'Employee Onboarding','Employee Promotion','Vehicle Log', 'Driver','Vehicle'): {
	  'validate': 'ploy_app.ploy_app.allot.hrm_status' 
	  },
  ('Loan Application', 'Loan', 'Loan Disbursement', 'Loan Repayment', 'Loan Write Off'): {
	  'validate': 'ploy_app.ploy_app.allot.loan_status'
	  },
  ('Payroll Entry', 'Salary Slip', 'Additional Salary', 'Employee Benefit Application', 'Employee Benefit Claim') : {
	  'validate': 'ploy_app.ploy_app.allot.payroll_status'
  },
  ('Project', 'Task', 'Project Template', 'Project Type', 'Timesheet', 'Activity Cost', 'Activity Type') : {
	  'validate': 'ploy_app.ploy_app.allot.project_status'
  },
  ('Issue', 'Issue Type', 'Warranty Claim', 'Serial No', 'Service Level Agreement', 'Maintenance Schedule', 'Maintenance Visit') : {
	  'validate': 'ploy_app.ploy_app.allot.care_status'
  }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ploy_app.tasks.all"
# 	],
# 	"daily": [
# 		"ploy_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"ploy_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ploy_app.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ploy_app.tasks.monthly"
# 	]
# }
scheduler_events = {
	"daily": [
		"ploy_app.tasks.daily"
	]
}

boot_session = "ploy_app.api.boot_session"
# Testing
# -------

# before_tests = "ploy_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ploy_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ploy_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ploy_app.auth.validate"
# ]

override_whitelisted_methods = {
	"frappe.utils.change_log.show_update_popup": "ploy_app.api.ignore_update_popup"
}

