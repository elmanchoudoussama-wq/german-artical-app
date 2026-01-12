[app]
title = German Artical Trainer
package.name = articaltrainer
package.domain = org.artical
source.dir = .
source.include_exts = py,png,jpg,kv,json,ttf
version = 0.1

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,arabic_reshaper,python-bidi,kivmob,android

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
icon.filename = %(source.dir)s/icon.png

# Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Android SDK/NDK
android.ndk = 25b
android.api = 31
android.minapi = 21

# ADMOB CRITICAL SETTINGS
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-9298331856947532~1106493604
android.gradle_dependencies = com.google.android.gms:play-services-ads:20.6.0
android.enable_androidx = True

# Java/Build Settings
android.accept_sdk_license = True
android.gradle_repositories = google(),mavenCentral()

[buildozer]
log_level = 2
warn_on_root = 1
