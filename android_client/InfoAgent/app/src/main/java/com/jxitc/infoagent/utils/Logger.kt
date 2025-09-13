package com.jxitc.infoagent.utils

import android.util.Log

object Logger {
    private const val TAG = "InfoAgent"
    
    fun d(message: String, tag: String = TAG) {
        Log.d(tag, message)
    }
    
    fun i(message: String, tag: String = TAG) {
        Log.i(tag, message)
    }
    
    fun w(message: String, throwable: Throwable? = null, tag: String = TAG) {
        if (throwable != null) {
            Log.w(tag, message, throwable)
        } else {
            Log.w(tag, message)
        }
    }
    
    fun e(message: String, throwable: Throwable? = null, tag: String = TAG) {
        if (throwable != null) {
            Log.e(tag, message, throwable)
        } else {
            Log.e(tag, message)
        }
    }
    
    fun v(message: String, tag: String = TAG) {
        Log.v(tag, message)
    }
}