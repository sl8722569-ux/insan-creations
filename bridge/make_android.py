#!/usr/bin/env python3
"""Write Android WebView projects + GitHub Actions into each product repo."""
from __future__ import annotations

from pathlib import Path
import shutil

APPS = [
    {
        "id": "jarvis",
        "name": "JARVIS",
        "label": "J.A.R.V.I.S",
        "package": "creations.insan.jarvis",
        "root": Path(r"C:\Users\shamu\JARVIS"),
        "url": "https://sl8722569-ux.github.io/jarvis-assitant/webapp/",
        "icon": Path(r"C:\Users\shamu\JARVIS\docs\icons\jarvis-192.png"),
        "apk": "JARVIS-Android.apk",
        "release": "v3.2.0-installers",
        "color": "0xFF0B1A3A",
    },
    {
        "id": "univista",
        "name": "UniVista",
        "label": "UniVista",
        "package": "creations.insan.univista",
        "root": Path(r"C:\Users\shamu\UNIVISTA"),
        "url": "https://sl8722569-ux.github.io/univista/web/",
        "icon": Path(r"C:\Users\shamu\UNIVISTA\web\icon-192.png"),
        "apk": "UniVista-Android.apk",
        "release": "android-apk",
        "color": "0xFF071018",
    },
    {
        "id": "vaani",
        "name": "Vaani",
        "label": "Vaani",
        "package": "creations.insan.vaani",
        "root": Path(r"C:\Users\shamu\UNIVERSAL-LANGUAGE-AI"),
        "url": "https://sl8722569-ux.github.io/universal-language-ai/web/",
        "icon": Path(r"C:\Users\shamu\UNIVERSAL-LANGUAGE-AI\web\icon-192.png"),
        "apk": "Vaani-Android.apk",
        "release": "android-apk",
        "color": "0xFF07060F",
    },
    {
        "id": "nexcode",
        "name": "NEXCODE",
        "label": "NEXCODE",
        "package": "creations.insan.nexcode",
        "root": Path(r"C:\Users\shamu\NEXCODE"),
        "url": "https://sl8722569-ux.github.io/nexcode/web/",
        "icon": Path(r"C:\Users\shamu\NEXCODE\web\icon-192.png"),
        "apk": "NEXCODE-Android.apk",
        "release": "android-apk",
        "color": "0xFF1E1E1E",
    },
    {
        "id": "study",
        "name": "StudyAssistant",
        "label": "Study Assistant",
        "package": "creations.insan.study",
        "root": Path(r"C:\Users\shamu\ai-study-assistant"),
        "url": "https://sl8722569-ux.github.io/ai-study-assistant/web/",
        "icon": Path(r"C:\Users\shamu\ai-study-assistant\web\icons\study-assistant-192.png"),
        "apk": "StudyAssistant-Android.apk",
        "release": "android-apk",
        "color": "0xFF0B1A3A",
    },
    {
        "id": "cricket",
        "name": "INSANCricket",
        "label": "INSAN CRICKET",
        "package": "creations.insan.cricket",
        "root": Path(r"C:\Users\shamu\INSAN-CRICKET"),
        "url": "https://sl8722569-ux.github.io/insan-cricket/web/",
        "icon": Path(r"C:\Users\shamu\INSAN-CRICKET\web\icon-192.png"),
        "apk": "INSAN-CRICKET-Android.apk",
        "release": "android-apk",
        "color": "0xFF020617",
    },
]

SETTINGS = """pluginManagement {{
  repositories {{ google(); mavenCentral(); gradlePluginPortal() }}
}}
dependencyResolutionManagement {{
  repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
  repositories {{ google(); mavenCentral() }}
}}
rootProject.name = "{name}"
include ':app'
"""

ROOT_GRADLE = """plugins {
  id 'com.android.application' version '8.5.2' apply false
}
"""

APP_GRADLE = """plugins {{
  id 'com.android.application'
}}
android {{
  namespace '{package}'
  compileSdk 34
  defaultConfig {{
    applicationId "{package}"
    minSdk 24
    targetSdk 34
    versionCode 1
    versionName "1.0-ea"
    buildConfigField "String", "WEB_URL", "\\"{url}\\""
  }}
  buildFeatures {{ buildConfig true }}
  compileOptions {{
    sourceCompatibility JavaVersion.VERSION_1_8
    targetCompatibility JavaVersion.VERSION_1_8
  }}
  buildTypes {{
    debug {{ debuggable true }}
    release {{
      minifyEnabled false
      signingConfig signingConfigs.debug
    }}
  }}
}}
"""

PROPS = """org.gradle.jvmargs=-Xmx1536m
android.useAndroidX=true
android.nonTransitiveRClass=true
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET"/>
  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
  <uses-permission android:name="android.permission.CAMERA"/>
  <uses-permission android:name="android.permission.RECORD_AUDIO"/>
  <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
  <uses-feature android:name="android.hardware.camera" android:required="false"/>
  <application
      android:label="{label}"
      android:icon="@mipmap/ic_launcher"
      android:usesCleartextTraffic="true"
      android:networkSecurityConfig="@xml/network_security_config"
      android:theme="@android:style/Theme.DeviceDefault.NoActionBar">
    <activity android:name=".MainActivity" android:exported="true"
        android:configChanges="orientation|screenSize|keyboardHidden|uiMode"
        android:windowSoftInputMode="adjustResize">
      <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
      </intent-filter>
    </activity>
  </application>
</manifest>
"""

NETSEC = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
  <base-config cleartextTrafficPermitted="true">
    <trust-anchors><certificates src="system"/></trust-anchors>
  </base-config>
</network-security-config>
"""

MAIN = """package {package};

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.os.Build;

public class MainActivity extends Activity {{
  private WebView web;
  private static final int REQ = 42;

  @Override
  protected void onCreate(Bundle savedInstanceState) {{
    super.onCreate(savedInstanceState);
    getWindow().setStatusBarColor({color});
    web = new WebView(this);
    web.setBackgroundColor({color});
    setContentView(web);
    WebSettings s = web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setDatabaseEnabled(true);
    s.setMediaPlaybackRequiresUserGesture(false);
    s.setAllowFileAccess(true);
    s.setLoadWithOverviewMode(true);
    s.setUseWideViewPort(true);
    if (Build.VERSION.SDK_INT >= 21) {{
      s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
    }}
    web.setWebViewClient(new WebViewClient());
    web.setWebChromeClient(new WebChromeClient() {{
      @Override
      public void onPermissionRequest(final PermissionRequest request) {{
        runOnUiThread(() -> request.grant(request.getResources()));
      }}
    }});
    web.setDownloadListener((url, ua, cd, mime, len) -> {{
      try {{
        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
        startActivity(i);
      }} catch (Exception ignored) {{}}
    }});
    requestPermissions(new String[] {{
      Manifest.permission.CAMERA,
      Manifest.permission.RECORD_AUDIO
    }}, REQ);
    web.loadUrl(BuildConfig.WEB_URL);
  }}

  @Override
  public void onBackPressed() {{
    if (web.canGoBack()) web.goBack();
    else super.onBackPressed();
  }}

  @Override
  public void onRequestPermissionsResult(int c, String[] p, int[] r) {{
    /* WebView will request again if needed */
  }}
}}
"""

WORKFLOW = """name: android-apk
on:
  workflow_dispatch:
  push:
    paths:
      - 'android/**'
      - '.github/workflows/android-apk.yml'
permissions:
  contents: write
jobs:
  apk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: '8.7'
      - name: Build APK
        working-directory: android
        run: gradle assembleRelease --no-daemon
      - name: Name artifact
        run: cp android/app/build/outputs/apk/release/app-release.apk {apk}
      - uses: actions/upload-artifact@v4
        with:
          name: {apk}
          path: {apk}
      - name: Attach to GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          TAG="{release}"
          if gh release view "$TAG" >/dev/null 2>&1; then
            gh release upload "$TAG" {apk} --clobber
          else
            gh release create "$TAG" {apk} --title "{label} Android APK" --notes "Sideload APK: official WebView of the live PWA (camera/mic allowed). Early Access, debug-signed. Not a Play Store listing."
          fi
"""

README = """# Android APK ({label})

Official **WebView wrapper** of the live PWA:

{url}

This is a real installable APK (camera + microphone permissions). It is **not** a rewrite of the Windows Python app.

Built by GitHub Actions (`.github/workflows/android-apk.yml`). Sideload the file from Releases.
"""


def patch_gitignore(root: Path) -> None:
    gi = root / ".gitignore"
    extra = "\n# Android build\nandroid/.gradle/\nandroid/build/\nandroid/app/build/\nandroid/local.properties\n"
    text = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if "android/.gradle/" not in text:
        gi.write_text(text.rstrip() + extra, encoding="utf-8")


def write_app(app: dict) -> None:
    root: Path = app["root"]
    android = root / "android"
    pkg_path = android / "app/src/main/java" / Path(*app["package"].split("."))
    res = android / "app/src/main/res"
    for p in (
        pkg_path,
        res / "mipmap-hdpi",
        res / "mipmap-mdpi",
        res / "mipmap-xhdpi",
        res / "mipmap-xxhdpi",
        res / "xml",
        root / ".github/workflows",
    ):
        p.mkdir(parents=True, exist_ok=True)

    (android / "settings.gradle").write_text(SETTINGS.format(**app), encoding="utf-8")
    (android / "build.gradle").write_text(ROOT_GRADLE, encoding="utf-8")
    (android / "gradle.properties").write_text(PROPS, encoding="utf-8")
    (android / "app/build.gradle").write_text(APP_GRADLE.format(**app), encoding="utf-8")
    (android / "app/src/main/AndroidManifest.xml").write_text(MANIFEST.format(**app), encoding="utf-8")
    (res / "xml/network_security_config.xml").write_text(NETSEC, encoding="utf-8")
    (pkg_path / "MainActivity.java").write_text(MAIN.format(**app), encoding="utf-8")
    (android / "README.md").write_text(README.format(**app), encoding="utf-8")
    wf = WORKFLOW.replace("{apk}", app["apk"]).replace("{release}", app["release"]).replace("{label}", app["label"])
    (root / ".github/workflows/android-apk.yml").write_text(wf, encoding="utf-8")
    icon = app["icon"]
    if icon.exists():
        for dens in ("mdpi", "hdpi", "xhdpi", "xxhdpi"):
            shutil.copyfile(icon, res / f"mipmap-{dens}/ic_launcher.png")
    patch_gitignore(root)
    print("wrote", android)


def main() -> None:
    for app in APPS:
        write_app(app)


if __name__ == "__main__":
    main()
