package com.jxitc.infoagent

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.jxitc.infoagent.presentation.screen.AddMemoryScreen
import com.jxitc.infoagent.presentation.screen.HomeScreen
import com.jxitc.infoagent.ui.theme.InfoAgentTheme

class MainActivity : ComponentActivity() {
    
    private val appContainer by lazy {
        (application as InfoAgentApplication).appContainer
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            InfoAgentTheme {
                InfoAgentApp(appContainer)
            }
        }
    }
}

@Composable
fun InfoAgentApp(appContainer: com.jxitc.infoagent.di.AppContainer) {
    val navController = rememberNavController()
    
    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(innerPadding)
        ) {
            composable("home") {
                HomeScreen(
                    onNavigateToAddMemory = {
                        navController.navigate("add_memory")
                    }
                )
            }
            
            composable("add_memory") {
                val viewModel = remember { appContainer.createAddMemoryViewModel() }
                AddMemoryScreen(
                    viewModel = viewModel,
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
        }
    }
}

