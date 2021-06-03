/*
 * Copyright (C) 2011-2013 GUIGUI Simon, fyhertz@gmail.com
 * 
 * This file is part of Spydroid (http://code.google.com/p/spydroid-ipcamera/)
 * 
 * Spydroid is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This source code is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this source code; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
package net.majorkernelpanic.spydroid

import android.app.Application
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.SharedPreferences.OnSharedPreferenceChangeListener
import android.os.Build
import android.preference.PreferenceManager
import net.majorkernelpanic.streaming.SessionBuilder
import net.majorkernelpanic.streaming.video.VideoQuality

class SpydroidApplication : Application() {
    /** Default quality of video streams.  */
    @JvmField
    var videoQuality = VideoQuality(640, 480, 15, 500000)

    /** By default AMR is the audio encoder.  */
    @JvmField
    var audioEncoder = SessionBuilder.AUDIO_AMRNB

    /** By default H.263 is the video encoder.  */
    @JvmField
    var videoEncoder = SessionBuilder.VIDEO_H263

    /** Set this flag to true to disable the ads.  */
    @JvmField
    val DONATE_VERSION = false

    /** If the notification is enabled in the status bar of the phone.  */
    @JvmField
    var notificationEnabled = true

    /** The HttpServer will use those variables to send reports about the state of the app to the web interface.  */
    @JvmField
    var applicationForeground = true
    @JvmField
    var lastCaughtException: Exception? = null

    /** Contains an approximation of the battery level.  */
    @JvmField
    var batteryLevel = 0
    override fun onCreate() {

        // The following line triggers the initialization of ACRA
        // Please do not uncomment this line unless you change the form id or I will receive your crash reports !
        //ACRA.init(this);
        instance = this
        super.onCreate()
        val settings = PreferenceManager.getDefaultSharedPreferences(this)
        notificationEnabled = settings.getBoolean("notification_enabled", true)

        // On android 3.* AAC ADTS is not supported so we set the default encoder to AMR-NB, on android 4.* AAC is the default encoder
        audioEncoder =
            if (Build.VERSION.SDK_INT.toInt() < 14) SessionBuilder.AUDIO_AMRNB else SessionBuilder.AUDIO_AAC
        audioEncoder = settings.getString("audio_encoder", audioEncoder.toString())!!.toInt()
        videoEncoder = settings.getString("video_encoder", videoEncoder.toString())!!.toInt()

        // Read video quality settings from the preferences 
        videoQuality = VideoQuality.merge(
            VideoQuality(
                settings.getInt("video_resX", 0),
                settings.getInt("video_resY", 0),
                settings.getString("video_framerate", "0")!!.toInt(),
                settings.getString("video_bitrate", "0")!!.toInt() * 1000
            ),
            videoQuality
        )
        SessionBuilder.getInstance()
            .setContext(applicationContext)
            .setAudioEncoder(if (!settings.getBoolean("stream_audio", true)) 0 else audioEncoder)
            .setVideoEncoder(
                if (!settings.getBoolean(
                        "stream_video",
                        false
                    )
                ) 0 else videoEncoder
            ).videoQuality =
            videoQuality

        // Listens to changes of preferences
        settings.registerOnSharedPreferenceChangeListener(mOnSharedPreferenceChangeListener)
        registerReceiver(mBatteryInfoReceiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
    }

    private val mOnSharedPreferenceChangeListener =
        OnSharedPreferenceChangeListener { sharedPreferences, key ->
            if (key == "video_resX" || key == "video_resY") {
                videoQuality.resX = sharedPreferences.getInt("video_resX", 0)
                videoQuality.resY = sharedPreferences.getInt("video_resY", 0)
            } else if (key == "video_framerate") {
                videoQuality.framerate =
                    sharedPreferences.getString("video_framerate", "0")!!.toInt()
            } else if (key == "video_bitrate") {
                videoQuality.bitrate =
                    sharedPreferences.getString("video_bitrate", "0")!!.toInt() * 1000
            } else if (key == "audio_encoder" || key == "stream_audio") {
                audioEncoder =
                    sharedPreferences.getString("audio_encoder", audioEncoder.toString())!!
                        .toInt()
                SessionBuilder.getInstance().audioEncoder = audioEncoder
                if (!sharedPreferences.getBoolean(
                        "stream_audio",
                        false
                    )
                ) SessionBuilder.getInstance().audioEncoder = 0
            } else if (key == "stream_video" || key == "video_encoder") {
                videoEncoder =
                    sharedPreferences.getString("video_encoder", videoEncoder.toString())!!
                        .toInt()
                SessionBuilder.getInstance().videoEncoder = videoEncoder
                if (!sharedPreferences.getBoolean(
                        "stream_video",
                        true
                    )
                ) SessionBuilder.getInstance().videoEncoder = 0
            } else if (key == "notification_enabled") {
                notificationEnabled = sharedPreferences.getBoolean("notification_enabled", true)
            }
        }
    private val mBatteryInfoReceiver: BroadcastReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            batteryLevel = intent.getIntExtra("level", 0)
        }
    }

    companion object {
        const val TAG = "SpydroidApplication"
        var instance: SpydroidApplication? = null
            private set
    }
}