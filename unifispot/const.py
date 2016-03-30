AUTH_TYPE_BYPASS    = 0
AUTH_TYPE_SPLASH    = 0
AUTH_TYPE_EMAIL   	= 1
AUTH_TYPE_VOUCHER   = 2
AUTH_TYPE_SOCIAL    = 4
AUTH_TYPE_SMS    	= 8
AUTH_TYPE_ALL		= 15


FORM_FIELD_FIRSTNAME	= 1
FORM_FIELD_LASTNAME		= 2
FORM_FIELD_EMAIL		= 4
FORM_FIELD_PHONE		= 8
FORM_FIELD_ALL			= 15


REDIRECT_ORIG_URL   = 1
REDIRECT_CUSTOM_URL = 2

FACEBOOK_LIKE_OFF   = 1
FACEBOOK_LIKE_OPNL  = 2
FACEBOOK_LIKE_REQ   = 3

FACEBOOK_POST_OFF   = 1
FACEBOOK_POST_OPNL  = 2
FACEBOOK_POST_REQ   = 3


SESSION_INIT            = 1
SESSION_AUTHORIZED      = 2
SESSION_TEMP_AUTH		= 3
SESSION_EXPIRED         = 4
SESSION_BAN             = 5

GUESTRACK_INIT          = 1 #Guesttrack creation
GUESTRACK_SESSION       = 2 #guesttrack is assigned a session
GUESTRACK_NO_AUTH       = 3 #guest track of no_auth site
GUESTRACK_NEW_AUTH      = 5 #newly authorized guest track
GUESTRACK_SOCIAL_PREAUTH= 6 #guesttrack devices previously authorized
GUESTRACK_VOUCHER_AUTH  = 7 #authorized by voucher
GUESTRACK_SOCIAL_AUTH  	= 8 #authorized by social login
GUESTRACK_EMAIL_AUTH  	= 9 #authorized by email

DEVICE_INIT             = 1
DEVICE_AUTH             = 2
DEVICE_SMS_AUTH         = 3
DEVICE_BAN              = 4
DEVICE_VOUCHER_AUTH     = 5

GUEST_INIT              = 1
GUEST_AUTHORIZED        = 2
GUEST_BANNED            = 3

ROLE_SUPERADMIN			= 1
ROLE_ADMIN				= 2
ROLE_CLIENT				= 3

CLIENT_REPORT_NONE		= 1
CLIENT_REPORT_WEEKLY	= 2
CLIENT_REPORT_MONTHLY	= 3

API_END_POINT_NONE		= 1
API_END_POINT_MAIL_CHIMP= 2
API_END_POINT_GRIND		= 3
API_END_POINT_COUNTER   = 4

SMS_DATA_NEW            = 1
SMS_CODE_SEND           = 2
SMS_CODE_USED           = 3


ACCOUNT_TYPE_FREE		= 1
ACCOUNT_TYPE_SILVER		= 2
ACCOUNT_TYPE_GOLD		= 3
ACCOUNT_TYPE_GOLD_PREM	= 4

font_list = ["Helvetica, sans-serif",
	"Verdana, sans-serif",
	"Gill Sans, sans-serif",
	"Avantgarde, sans-serif",
	"Helvetica Narrow, sans-serif",
	"Times, serif",
	"Times New Roman, serif",
	"Palatino, serif",
	"Bookman, serif",
	"New Century Schoolbook, serif",
	"Andale Mono, monospace",
	"Courier New, monospace",
	"Courier, monospace",
	"Lucidatypewriter, monospace",
	"Fixed, monospace",
	"Comic Sans, Comic Sans MS, cursive",
	"Zapf Chancery, cursive",
	"Coronetscript, cursive",
	"Florence, cursive",
	"Parkavenue, cursive",
	"Impact, fantasy",
	"Arnoldboecklin, fantasy",
	"Oldtown, fantasy",
	"Blippo, fantasy",
	"Brushstroke, fantasy",
	"MrsEavesXLSerNarOT-Reg",
	"Georgia, serif"]