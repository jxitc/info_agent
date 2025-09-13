package com.jxitc.infoagent.data.remote

import com.jxitc.infoagent.data.local.AppPreferences
import com.jxitc.infoagent.domain.model.Memory
import com.jxitc.infoagent.domain.model.MemoryCreationRequest
import com.jxitc.infoagent.domain.model.ProcessingResult
import com.jxitc.infoagent.utils.Logger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

class InfoAgentApiClient(
    private val preferences: AppPreferences
) {
    
    private val loggingInterceptor = HttpLoggingInterceptor { message ->
        Logger.d(message, "API")
    }.apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private fun createApiService(): InfoAgentApiService {
        val retrofit = Retrofit.Builder()
            .baseUrl(preferences.serverUrl.ensureTrailingSlash())
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        return retrofit.create(InfoAgentApiService::class.java)
    }
    
    suspend fun createMemory(request: MemoryCreationRequest): ProcessingResult<Memory> {
        return withContext(Dispatchers.IO) {
            try {
                val apiService = createApiService()
                val apiRequest = CreateMemoryRequest(
                    content = request.content,
                    title = null // Let server generate title
                )
                
                Logger.d("Creating memory on server: ${request.content.take(50)}...")
                
                val response = apiService.createMemory(apiRequest)
                
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body?.status == "success" && body.data != null) {
                        val memory = body.data.toDomainModel()
                        Logger.i("Memory created on server: ID ${memory.id}")
                        ProcessingResult.Success(memory)
                    } else {
                        val errorMsg = body?.error?.message ?: "Unknown server error"
                        Logger.e("Server error: $errorMsg")
                        ProcessingResult.Error("Server error: $errorMsg")
                    }
                } else {
                    val errorMsg = "HTTP ${response.code()}: ${response.message()}"
                    Logger.e("API error: $errorMsg")
                    ProcessingResult.Error("Network error: $errorMsg")
                }
            } catch (e: Exception) {
                Logger.e("Failed to create memory on server: ${e.message}", e)
                ProcessingResult.Error("Connection failed: ${e.message}")
            }
        }
    }
    
    suspend fun getMemories(limit: Int = 50, offset: Int = 0): ProcessingResult<List<Memory>> {
        return withContext(Dispatchers.IO) {
            try {
                val apiService = createApiService()
                
                Logger.d("Fetching memories from server (limit: $limit, offset: $offset)")
                
                val response = apiService.getMemories(limit, offset)
                
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body?.status == "success" && body.data != null) {
                        val memories = body.data.memories.map { it.toDomainModel() }
                        Logger.i("Fetched ${memories.size} memories from server")
                        ProcessingResult.Success(memories)
                    } else {
                        val errorMsg = body?.error?.message ?: "Unknown server error"
                        Logger.e("Server error: $errorMsg")
                        ProcessingResult.Error("Server error: $errorMsg")
                    }
                } else {
                    val errorMsg = "HTTP ${response.code()}: ${response.message()}"
                    Logger.e("API error: $errorMsg")
                    ProcessingResult.Error("Network error: $errorMsg")
                }
            } catch (e: Exception) {
                Logger.e("Failed to fetch memories from server: ${e.message}", e)
                ProcessingResult.Error("Connection failed: ${e.message}")
            }
        }
    }
    
    suspend fun healthCheck(): ProcessingResult<Boolean> {
        return withContext(Dispatchers.IO) {
            try {
                val apiService = createApiService()
                
                Logger.d("Checking server health at ${preferences.serverUrl}")
                
                val response = apiService.healthCheck()
                
                if (response.isSuccessful) {
                    Logger.i("Server health check passed")
                    ProcessingResult.Success(true)
                } else {
                    val errorMsg = "HTTP ${response.code()}: ${response.message()}"
                    Logger.e("Health check failed: $errorMsg")
                    ProcessingResult.Error("Health check failed: $errorMsg")
                }
            } catch (e: Exception) {
                Logger.e("Health check failed: ${e.message}", e)
                ProcessingResult.Error("Server unreachable: ${e.message}")
            }
        }
    }
    
    private fun String.ensureTrailingSlash(): String {
        return if (this.endsWith("/")) this else "$this/"
    }
}