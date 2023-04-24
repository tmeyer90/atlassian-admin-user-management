ORG_BASE_URL = 'https://api.atlassian.com'
GET_ORGS = ORG_BASE_URL + '/admin/v1/orgs'
GET_ORG = ORG_BASE_URL + '/admin/v1/orgs/<ORG_ID>'
GET_USERS = GET_ORG + '/users'
SITE_BASE_URL = 'https://<SITE>.atlassian.net'
GET_JIRA_APPS = SITE_BASE_URL + '/rest/plugins/1.0/'
GET_CONF_APPS = SITE_BASE_URL + '/wiki/rest/plugins/1.0/'
GET_MYSELF = SITE_BASE_URL + '/rest/api/3/myself'
GET_JIRA_APP_LICENSE = SITE_BASE_URL + '/rest/plugins/1.0/<APP_KEY>-key/license'
GET_CONF_APP_LICENSE = SITE_BASE_URL + '/wiki/rest/plugins/1.0/<APP_KEY>-key/license'



