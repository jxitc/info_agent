package com.jxitc.infoagent.domain.service

import com.jxitc.infoagent.data.local.AppPreferences
import com.jxitc.infoagent.data.remote.InfoAgentApiClient
import com.jxitc.infoagent.domain.model.Memory
import com.jxitc.infoagent.domain.model.MemoryCreationRequest
import com.jxitc.infoagent.domain.model.ProcessingResult
import com.jxitc.infoagent.domain.repository.MemoryRepository
import com.jxitc.infoagent.utils.Logger
import kotlinx.coroutines.flow.first

class MemorySyncService(
    private val memoryRepository: MemoryRepository,
    private val apiClient: InfoAgentApiClient,
    private val appPreferences: AppPreferences
) {
    
    /**
     * Syncs all pending memories to the server
     * @return Pair<uploaded count, failed count>
     */
    suspend fun syncPendingMemories(): Pair<Int, Int> {
        if (!appPreferences.autoSync) {
            Logger.i("Auto-sync disabled, skipping sync")
            return Pair(0, 0)
        }
        
        Logger.i("Starting sync of pending memories...")
        
        val pendingMemories = try {
            memoryRepository.getPendingUploads().first()
        } catch (e: Exception) {
            Logger.e("Failed to get pending uploads", e)
            return Pair(0, 0)
        }
        
        if (pendingMemories.isEmpty()) {
            Logger.i("No pending memories to sync")
            return Pair(0, 0)
        }
        
        Logger.i("Found ${pendingMemories.size} pending memories to sync")
        
        var uploadedCount = 0
        var failedCount = 0
        
        for (memory in pendingMemories) {
            try {
                val success = syncSingleMemory(memory)
                if (success) {
                    uploadedCount++
                    Logger.i("Successfully synced memory ${memory.id}: '${memory.title}'")
                } else {
                    failedCount++
                    Logger.w("Failed to sync memory ${memory.id}: '${memory.title}'")
                }
            } catch (e: Exception) {
                failedCount++
                Logger.e("Exception syncing memory ${memory.id}: '${memory.title}'", e)
                
                // Increment retry count for failed uploads
                memoryRepository.incrementRetryCount(memory.id)
            }
        }
        
        Logger.i("Sync completed: $uploadedCount uploaded, $failedCount failed")
        return Pair(uploadedCount, failedCount)
    }
    
    private suspend fun syncSingleMemory(memory: Memory): Boolean {
        // Skip memories that have failed too many times
        if (memory.uploadRetryCount >= MAX_RETRY_COUNT) {
            Logger.w("Memory ${memory.id} exceeded max retry count (${memory.uploadRetryCount}), skipping")
            return false
        }
        
        val request = MemoryCreationRequest(
            content = memory.content,
            sourceType = memory.sourceType,
            metadata = memory.metadata
        )
        
        return when (val result = apiClient.createMemory(request)) {
            is ProcessingResult.Success -> {
                // Successfully uploaded - mark as uploaded in local database
                memoryRepository.updateMemoryUploadStatus(memory.id, true)
                true
            }
            is ProcessingResult.Error -> {
                Logger.w("Server rejected memory ${memory.id}: ${result.message}")
                // Increment retry count but don't mark as uploaded
                memoryRepository.incrementRetryCount(memory.id)
                false
            }
            ProcessingResult.Loading -> {
                // This shouldn't happen in our current implementation
                Logger.w("Unexpected loading state for memory ${memory.id}")
                false
            }
        }
    }
    
    companion object {
        private const val MAX_RETRY_COUNT = 5
    }
}