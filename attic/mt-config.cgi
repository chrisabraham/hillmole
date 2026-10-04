## Movable Type configuration file [mt-config.cgi]             ##
##                                                             ##
## This configuration file holds system-wide configuration     ##
## settings that apply to *all* of the blogs in your Movable   ##
## Type installation.                                          ##
##                                                             ##
## Most system directives are listed below although many are   ##
## commented out, meaning they use the internal default value. ##
##                                                             ##
## Anything following a '#' is ignored by the system when the  ##
## configuration is read.  To enable a directive and assign    ##
## its value in the system, simply remove the '#' preceding    ##
## it.  First, however, make sure that you understand the      ##
## purpose of the configuration setting.                       ##

##                      IMPORTANT                              ##
## If you are installing Movable Type for the first time, you  ##
## should read the Installation section of the documentation   ##
## at http://www.sixapart.com/movabletype/docs/3.2/            ##


# Movable Type uses the CGIPath setting to construct links back to
# CGI scripts; for example, the MT tag <$MTCGIPath$> is substituted
# with the value of the CGIPath setting.  You will need to change this
# value when you first install MT.  This should be set to the URL 
# used to access mt.cgi but *without* mt.cgi appended to the end. 

CGIPath http://www.hillmole.com/


### MySQL Configuration - Add the name of your database, username
# password and, optionally database host given to you by your web 
# hosting provider.
#
ObjectDriver DBI::mysql
Database REMOVED
DBUser REMOVED
DBPassword REMOVED
DBHost REMOVED
#
#
### PostgreSQL Configuration - Add the name of your database, username,
# password and, optionally database host given to you by your web 
# hosting provider.
#
# ObjectDriver DBI::postgres
# Database <database-name>
# DBUser <database-username>
# DBPassword <database-password>
# DBHost localhost
#
#
### SQLite Configuration - SQLite requires only the path to your SQLite
# database file.
#
# ObjectDriver DBI::sqlite
# Database /path/to/sqlite/database/file
#
#
### BerkeleyDB Configuration - BerekelyDB requires only the path to your
# database directory.
#
# DataSource  /path/to/database/directory
#
#
# ThrottleSeconds is the minimum number of seconds between comments
# from a single IP address. Setting this to 0 will turn off the
# throttling feature, which may make you vulnerable to
# comment-flooding. The default is 20.
#
# ThrottleSeconds 20
#
# MT needs to have an email address, from which it can send notification
# emails. This defaults to your author address, but some spam filters
# will reject emails that are From: and To: the same address. If you
# have another address you can use it here.
#
# EmailAddressMain you@alternate-email.com
#
#
# If you place all of your MT files in a cgi-bin directory, you
# will need to place the directory containing your static files
# (mt-static) elsewhere, so that the webserver will not try to execute
# them.  StaticWebPath is the path to your mt-static directory.
#
# StaticWebPath http://www.example.com/mt-static
#
#
# If you have downloaded the help documentation and want to refer
# to it within your MT installation, you can customize the HelpURL
# setting to point to your local copy.
#
# HelpURL http://www.example.com/mt-static/docs/
#
#
# The filesystem path to the 'tmpl' directory, which contains the
# front-end templates used by the Movable Type application. This
# setting defaults to './tmpl', which means that the 'tmpl' directory
# is in the same directory as the 'mt.cgi' file; you probably don't
# need to change this setting.
#
# TemplatePath ./tmpl
#
#
# By default, Movable Type looks for sendmail in three locations:
# /usr/lib/sendmail, /usr/sbin/sendmail, and /usr/ucblib/sendmail.
# If your sendmail is in a different location, you can adjust the
# SendMailPath configuration setting.
#
# SendMailPath /usr/sbin/sendmail
#
#
# If you would rather use SMTP than sendmail, you should set the
# MailTransfer config setting to 'smtp' (as below). You will also
# need to set the address of your SMTP server, and install the
# Mail::Sendmail Perl module. See the TROUBLESHOOTING section of the
# manual for more details. Possible values for MailTransfer are:
# 'smtp', 'sendmail', and 'debug' (which just writes out mail messages
# to STDERR, for debugging purposes). The default is 'sendmail'.
#
# MailTransfer smtp
# SMTPServer smtp.your-site.com
#
#
# By default, when writing to an output file (for example, one of your
# index or archive pages), Movable Type will first write the data to
# a temp file, then rename that temp file. In the case that the process
# writing the data dies unexpectedly, this prevents the pages on your
# site from being erased. If you do not like this behavior (because it
# requires you to set directory permissions too loosely, for example),
# uncomment the following setting.
#
# NoTempFiles 1
#
#
# The WeblogsPingURL setting is the URL used to send the XML-RPC
# weblogs.com ping. You should not need to change this setting unless
# weblogs.com announces that the URL is changing.
#
# WeblogsPingURL http://some.alternate.weblogs.com.server/path/
#
#
# The BlogsPingURL setting is the URL used to send the XML-RPC
# blo.gs ping. You should not need to change this setting unless
# blo.gs announces that the URL is changing.
#
# BlogsPingURL http://some.alternate.blo.gs.server/path/
#
#
# The MTPingURL setting is the URL used to send the XML-RPC ping to
# movabletype.org (if you have a Recently Updated Key). You should not
# need to change this setting.
#
# MTPingURL http://some.alternate.movabletype.org.server/path/
#
#
# When uploading files through Movable Type's upload mechanism, a ceiling
# is put on the size of the files that can be uploaded to prevent
# denial-of-service attacks. By default this setting is 1000000 (1MB).
#
# CGIMaxUpload 500000
#
#
# When creating files and directories, Movable Type uses umask settings to
# control the permissions set on the files. The default settings for file
# creation (HTMLUmask, DBUmask, and UploadUmask) are 0111; for directory
# creation (DirUmask), the default is 0000. You should not change these
# settings unless you are running MT under cgiwrap or suexec, or some other
# scenario where the MT application runs as you; in addition, you should not
# change these settings unless you know what they mean, and what they do.
#
# DBUmask 0022
# HTMLUmask 0022
# UploadUmask 0022
# DirUmask 0022
#
#
# In addition to controlling permissions via umask settings, you can also
# use the HTMLPerms and UploadPerms settings to control the default
# permissions for files created by the system (either as output files or
# uploaded files). The only real use of this is to turn on the executable bit
# of files created by the system--for example, if MT is generating PHP files
# that need to have the executable bit turned on, you could set HTMLPerms
# to 0777. The default is 0666. You should not change these settings unless
# you know what they mean, and what they do.
#
# HTMLPerms 0777
# UploadPerms 0777
#
#
# When processing uploaded files, if Movable Type notices that the file you
# uploaded already exists, it will allow you to overwrite the original file,
# by first asking for your confirmation. To do this, MT needs to write the
# uploaded data to a temporary file. That temporary file is stored in the
# directory specified by the TempDir setting; the value defaults to /tmp.
#
# TempDir /tmp/
#
#
# When rebuilding individual archives, Movable Type splits up the rebuilding
# process into segments, where each segment consists of rebuilding N entries.
# The default value for N is 40, so by default, MT will rebuild 40 entries at
# a time, then move on to the next 40, etc. You can change that value globally
# here; for example, if you have a very stable server, you might wish to just
# get it all done with in one batch.
#
# EntriesPerRebuild 40
#
#
# The filesystem path to the 'import' directory, which is used when importing
# entries and comments into the system--'import' is the directory where the
# files to be imported are placed. This setting defaults to './import', which
# means that the 'import' directory is in the same directory as the 'mt.cgi'
# file; you probably don't need to change this setting.
#
# ImportPath ./import
#
#
# By default Movable Type uses Perl's flock() function to lock your
# databases while reading and writing. On systems using NFS-mounted
# directories, however, Perl's flock() may fail, unless the perl executable
# has been built to use fnctl(2) instead of flock(2); and even then, it is
# not certain that the locking will truly work.
# Thus, if you have problems running Movable Type on systems using NFS, you
# can use this directive to use simpler file locking that will work over NFS.
# Note that this setting only applies if you are using the Berkeley DB
# version of MT.
#
# NOTE: do not adjust this setting unless you know what you are doing!
#
# UseNFSSafeLocking 1
#
#
# On some Windows systems, neither flock() nor link() are available, so
# you can't use the default flock() locking, nor can you use the NFS-safe 
# locking. In such cases, you can turn on the NoLocking option. Note that
# you should ONLY do this if your system supports nothing else--it is a
# last resort, because it increases the likelihood of database corruption.
# However, if you are the only person using the system (for example, if this
# is your personal server), this should not be as much of an issue.
# Note that this setting only applies if you are using the Berkeley DB
# version of MT.
#
# NOTE: do not adjust this setting unless you know what you are doing!
#
# NoLocking 1
#
#

DefaultLanguage en_US

# By default Movable Type uses the UTF-8 character encoding which
# supports an international range of characters. For some languages,
# though, UTF-8 is not he ideal encoding. Many Japanese users prefer
# Shift_JIS. Use the PublishCharset option to determine the character
# encoding that is sent in the HTTP headers.

PublishCharset utf-8
# PublishCharset Shift_JIS

# If you change the PublishCharset option, you may also need to resort
# to HTML entities (below) to encode characters that don't fall in your
# character set. 

# Normally, Movable Type will trust the character encoding to handle
# all text; but if you prefer to use HTML entities (for example, if
# you change the character encoding to a non-Unicode encoding), you
# should set the value of NoHTMLEntities to 0.  # You might also turn
# off this option if your system does not have the HTML::Entities Perl
# module installed.

NoHTMLEntities 1

#
# By default, when encoding data for XML Movable Type checks whether your
# data looks like it contains any HTML tags or other unsafe-for-XML data,
# and if so, it encloses your data in CDATA tags. Some news aggregators
# have trouble with combinations of CDATA with other data, though, so if
# this is causing a problem for you, you can use NoCDATA to encode any
# special characters into entities.
#
# NoCDATA 1
#
#
# When sending pings--either TrackBack pings or update pings--Movable Type
# sets a timeout on the ping, so that it doesn't take too long and appear to
# freeze up the system. You can override the default setting of 15 seconds
# by setting a different value with the PingTimeout directive. The value
# is assumed to be in seconds.
#
# PingTimeout 20
#
#
# By default, outgoing Trackback and update pings are sent to the internet
# using the default network interface card (NIC) on the server running
# Movable Type. In some rare cases, it may be necessary or desirable to have
# the outbound ping traffic sent over a different network interface card or
# network connection. In these situations, enter the IP address of the
# network interface card that should be used to send the outgoing ping
# notifications.
#
# You may specifiy only the IP address (xxx.xxx.xxx.xxx), or and IP address
# and port number (xxx.xxx.xxx.xxx:#). If no port number is specified, the
# outgoing ping will be sent from the specified IP address using the next
# available port number. If a port is specified, the outgoing ping will be
# sent from the specified IP address AND port number. This is useful when you
# need a consistent source IP:port address for firewall filtering of
# outbound connections.
#
# Note: Don't specify a port unless it's absolutely necessary. If the
# port specified is already in use, the outgoing ping will fail without
# error.
# 
# PingInterface 192.168.10.5
# PingInterface 192.168.10.5:8080
#
#
# In some cases, a proxy server must be used to gain access to the internet
# if the computer Movable Type is running on is behind a firewall or on an
# internal private network. By setting PingProxy to the full URL
# address of your proxy server, Movable Type will route all Trackback and
# update pings through the proxy server specified.
#
# PingProxy http://192.168.10.5:3128
#
#
# If PingProxy above is set, Movable Type will route Trackback and update
# pings through the specified proxy EXCEPT for pings destined for the domains
# listed in PingNoProxy. The default value is "localhost, 127.0.0.1"
#
# PingNoProxy internal.lan, example.tld
#
#
# Specifies the image toolkit used to create thumbnails from uploaded images.
# By default, the ImageMagick library and Image::Magick Perl module are used;
# if your system does not have these, you can use the NetPBM tools instead
# (assuming that your system has these tools installed). Possible values for
# this setting are "ImageMagick" or "NetPBM".
#
# ImageDriver NetPBM
#
#
# By default, Movable Type looks for the NetPBM tools in three locations:
# /usr/local/netpbm/bin, /usr/local/bin, and /usr/bin. If your
# NetPBM tools are installed in a different location, you can adjust the
# NetPBMPath configuration setting. Note that this path should be the path
# to the directory containing the NetPBM binaries; for example, if your
# pnmscale binary is at /home/foo/netpbm/bin/pnmscale, you should
# set the value of NetPBMPath to /home/foo/netpbm/bin.
#
# NetPBMPath /home/foo/netpbm/bin
#
#
# By default, the script that Movable Type uses for comments is called
# mt-comments.cgi, the TrackBack script is called mt-tb.cgi, the
# search engine script is called mt-search.cgi, the XML-RPC server
# script is called mt-xmlrpc.cgi, and the dynamic blog view script is
# called F<mt-view.cgi>. In
# some situations--for example, if you are running MT under mod_perl, or if
# your server requires that your Perl scripts have the extension .pl--you
# may need different names for these scripts. You can set the names that will
# be used throughout the default templates and Movable Type code by changing
# these values.
#
# AdminScript mt.pl
# CommentScript mt-comments.pl
# TrackbackScript mt-tb.pl
# SearchScript mt-search.pl
# XMLRPCScript mt-xmlrpc.pl
# ViewScript mt-view.pl
# AtomScript mt-atom.pl
# UpgradeScript mt-upgrade.pl
#
#
#
# "Safe mode" enables certain warnings about security and other issues,
# and turns off some small features and capabilities (for example, linking
# templates to files with .cgi and other extensions). Safe mode is on by
# default; you can turn it off by setting SafeMode to 0.
#
# SafeMode 0
#
#
# By default, Movable Type cleans up ("sanitizes") any data submitted by
# visitors to your site. This is done to remove any code (HTML or otherwise)
# that could compromise the security of your site. The sanitization code works
# by only allowing certain HTML tags--any other tags, and all processing
# instructions (PHP, for example) are stripped. The GlobalSanitizeSpec
# setting, then, specifies the tags and attributes that are allowed. The
# default setting is "a href,b,br/,p,strong,em,ul,li,blockquote".
#
# GlobalSanitizeSpec br/,p
#
#
# By default, for each TrackBack item in your Movable Type system--either
# entry or category TrackBack items--an individual RSS feed will be
# automatically created and managed, listing the TrackBack pings for that
# item. These pings are stored in your Local Archive Path. If you want to
# turn off this feature, you can set GenerateTrackBackRSS to 0.
# The default setting is 1, to generate RSS files for each TrackBack item.

GenerateTrackBackRSS 0


##
## Search configuration
##

# The filesystem path to the 'search_templates' directory, which is where
# your search templates should be located. This setting defaults to
# './search_templates', which means that the 'search_templates' directory
# is in the same directory as the 'mt.cgi' file; you probably don't need
# to change this setting, unless you have moved your 'search_templates'
# directory.
#
# SearchTemplatePath ./search_templates/
#
#
# The filename of the default search template, located inside of your
# 'search_templates' directory (see the SearchTemplatePath directive). If you
# define and use alternate templates (see below), you don't need to use
# the default template. The default value is 'default.tmpl'.
#
# DefaultTemplate default.tmpl
#
#
# If you have multiple blogs, or if you provide several different versions
# of your site, you may wish to use alternate templates to provide different
# versions of your search results, as well. See "Alternate Templates" in
# the manual for more details. You can define as many alternate templates
# as you want.

AltTemplate comments comments.tmpl
# AltTemplate work work.tmpl
# AltTemplate play play.tmpl
#
#
# To restrict the blogs included in a search on your site, you can use the
# IncludeBlogs and ExcludeBlogs settings. IncludeBlogs lists the blogs that
# will be included in the search, and ExcludeBlogs lists blogs that will be
# excluded from the search. Do not try to use both--IncludeBlogs will
# override ExcludeBlogs. The default is to search all blogs. Separate blog
# IDs with commas.
#
# ExcludeBlogs 1,3,4
# IncludeBlogs 2
#
#
# The following settings specify the defaults for searches on your site;
# they can be overridden either through hidden form inputs, or in form inputs
# set by your users. You should probably leave these settings at the defaults
# and allow your users to override them. RegexSearch is a regular-expression
# search, and CaseSearch is a case-sensitive search. The default value for
# each of these settings is 0.
#
# RegexSearch 1
# CaseSearch 1
#
#
# The default number of days to search on a regular search (SearchCutoff)
# or on a new comment search (CommentSearchCutoff). The default for
# SearchCutoff is to search from the beginning of your blog (all of your
# entries), and the default for CommentSearchCutoff is the last month of
# comments.
#
# SearchCutoff 7
# CommentSearchCutoff 7
#
#
# The maximum number of results to return in a search. If this is a straight
# search, the number of results is per-blog--if you set MaxResults to 5,
# for example, that would mean a maximum of 5 results for each blog in your
# system. In a new comment search, this is the maximum number of entries
# with new comments.
#
# MaxResults 5
#
#
# The sort order for the search results. Using 'ascend' will list the entries
# in chronological order (oldest entry at the top); using 'descend' will
# list the entries in reverse chronological order (newest entry at the top).
# The default is 'descend'.
#
# ResultDisplay ascend
#
#
# The number of words in the excerpt displayed when you use the
# <$MTEntryExcerpt$> tag inside of your search results. This setting is
# distinct from the "Number of words in excerpt" setting in your blog
# configuration, because this setting is just used for excerpts in your
# search results. The default is 40 words.
#
# ExcerptWords 100
#
#
# By default, a search will search only through the entries in your blog,
# not through the comments. A comment search is slower than an entry search,
# because there is more text to search through. You should probably leave
# this set to 'entries', and let your visitors override that setting if
# they wish to. Possible values are 'entries', 'comments', or 'both'.
#
# SearchElement both
#
#
# By default, the search engine allows most of the above configuration
# directives to be overridden by search templates. This has the side effect
# that users could also override those settings by changing values in the
# query string. In particular, this could be dangerous if you have some
# private weblogs--even if you use IncludeBlogs or ExcludeBlogs to
# allow/deny certain weblogs to be searched, users could override that
# setting to search your private weblog. You can use NoOverride to provide
# a comma-separated list of configuration directives that cannot be
# overriden by either search templates or users. This means that only the
# settings made in mt.cfg will be used.
#
# NoOverride IncludeBlogs,ExcludeBlogs
#
# By default, Movable Type won't try to do rebuilds and other
# time-consuming activies in the background. If you want to improve
# your experience at rebuild time, try setting LaunchBackgroundTasks
# to 1. Note that this will cause problems on some installations and
# should be turned off if you experience crashes.

LaunchBackgroundTasks 0

#
# The TypeKey protocol has been revised. The latest version is highly
# recommended, however, for users who haven't updated their templates,
# This option can be set to a backward-compatible value.

TypeKeyVersion 1.1

# The DebugMode option controls whether Movable Type runs in a debugging
# operational state. When DebugMode is 1, Perl warnings are displayed on
# web pages. DebugMode of 0 (the default) suppresses these warnings.

DebugMode 0

