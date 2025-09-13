package com.jxitc.infoagent.data.remote

import retrofit2.Response
import retrofit2.http.*

interface InfoAgentApiService {
    
    @POST("api/v1/memories")
    suspend fun createMemory(
        @Body request: CreateMemoryRequest
    ): Response<ApiResponse<MemoryApiResponse>>
    
    @GET("api/v1/memories")
    suspend fun getMemories(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0
    ): Response<ApiResponse<MemoryListResponse>>
    
    @GET("api/v1/memories/{id}")
    suspend fun getMemory(
        @Path("id") id: Long
    ): Response<ApiResponse<MemoryApiResponse>>
    
    @DELETE("api/v1/memories/{id}")
    suspend fun deleteMemory(
        @Path("id") id: Long
    ): Response<ApiResponse<Map<String, Any>>>
    
    @GET("health")
    suspend fun healthCheck(): Response<Map<String, Any>>
}