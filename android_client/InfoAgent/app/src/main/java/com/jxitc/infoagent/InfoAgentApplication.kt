package com.jxitc.infoagent

import android.app.Application
import com.jxitc.infoagent.di.AppContainer

class InfoAgentApplication : Application() {
    
    val appContainer: AppContainer by lazy {
        AppContainer(this)
    }
}