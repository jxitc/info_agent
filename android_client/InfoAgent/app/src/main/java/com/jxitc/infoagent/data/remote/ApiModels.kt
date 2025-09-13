package com.jxitc.infoagent.data.remote

import com.google.gson.annotations.SerializedName
import com.jxitc.infoagent.domain.model.Memory
import com.jxitc.infoagent.domain.model.SourceType
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

// Request models
data class CreateMemoryRequest(
    @SerializedName("content")
    val content: String,
    @SerializedName("title")
    val title: String? = null
)

// Response models
data class ApiResponse<T>(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("message")
    val message: String? = null,
    @SerializedName("data")
    val data: T? = null,
    @SerializedName("error")
    val error: ApiError? = null
)

data class ApiError(
    @SerializedName("code")
    val code: String,
    @SerializedName("message")
    val message: String
)

data class MemoryApiResponse(
    @SerializedName("id")
    val id: Long,
    @SerializedName("title")
    val title: String,
    @SerializedName("content")
    val content: String,
    @SerializedName("word_count")
    val wordCount: Int,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("updated_at")
    val updatedAt: String? = null,
    @SerializedName("dynamic_fields")
    val dynamicFields: Map<String, Any>? = null
)

data class MemoryListResponse(
    @SerializedName("memories")
    val memories: List<MemoryApiResponse>,
    @SerializedName("total")
    val total: Int,
    @SerializedName("has_more")
    val hasMore: Boolean
)

// Extension functions for conversion
fun MemoryApiResponse.toDomainModel(): Memory {
    val createdAtParsed = try {
        LocalDateTime.parse(createdAt.removeSuffix("Z"), DateTimeFormatter.ISO_LOCAL_DATE_TIME)
    } catch (e: Exception) {
        LocalDateTime.now()
    }
    
    val updatedAtParsed = try {
        updatedAt?.let { 
            LocalDateTime.parse(it.removeSuffix("Z"), DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        } ?: createdAtParsed
    } catch (e: Exception) {
        createdAtParsed
    }
    
    return Memory(
        id = id,
        title = title,
        content = content,
        sourceType = SourceType.MANUAL, // Server memories are considered manual for now
        metadata = dynamicFields?.mapValues { it.value?.toString() ?: "" } ?: emptyMap(),
        createdAt = createdAtParsed,
        updatedAt = updatedAtParsed,
        isUploaded = true, // Already on server
        uploadRetryCount = 0
    )
}