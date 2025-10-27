/**
 * Schema Validator Pro - Metabox JavaScript
 * Handles schema generation in the post editor
 */

(function($) {
    'use strict';

    // Retry configuration
    var RETRY_CONFIG = {
        maxRetries: 2,  // Maximum number of retries (total 3 attempts)
        baseDelay: 1000,  // Initial delay in milliseconds
        maxDelay: 10000,  // Maximum delay in milliseconds
        retryableStatusCodes: [500, 502, 503, 504, 0]  // 5xx errors and network failures
    };

    /**
     * Initialize metabox functionality
     */
    function initMetabox() {
        var $generateBtn = $('#svp-generate-schema-btn');
        var $status = $('#svp-schema-status');
        var $schemaType = $('#svp_schema_type');

        if (!$generateBtn.length) {
            return;
        }

        // Handle generate button click
        $generateBtn.on('click', function(e) {
            e.preventDefault();
            generateSchema();
        });

        /**
         * Generate schema via AJAX with retry logic
         */
        function generateSchema(attemptNumber) {
            attemptNumber = attemptNumber || 0;

            var schemaType = $schemaType.val();
            var postId = svpMetaboxData.postId;
            var nonce = svpMetaboxData.nonce;

            // Disable button and show loading state
            var loadingText = attemptNumber > 0
                ? svpMetaboxData.i18n.retrying + ' (' + (attemptNumber + 1) + '/' + (RETRY_CONFIG.maxRetries + 1) + ')'
                : svpMetaboxData.i18n.generating;

            $generateBtn.prop('disabled', true).text(loadingText);
            $status.html('<span class="svp-status-loading">' + svpMetaboxData.i18n.generatingMessage + '</span>');

            // Make AJAX request
            $.ajax({
                url: ajaxurl,
                type: 'POST',
                data: {
                    action: 'svp_generate_schema',
                    post_id: postId,
                    schema_type: schemaType,
                    _wpnonce: nonce
                },
                timeout: 30000,  // 30 second timeout
                success: function(response) {
                    handleSuccess(response);
                },
                error: function(xhr, status, error) {
                    handleError(xhr, status, error, attemptNumber);
                }
            });
        }

        /**
         * Handle successful response
         */
        function handleSuccess(response) {
            if (response.success) {
                $status.html('<span class="svp-status-success">✓ ' + response.data.message + '</span>');
                
                // Reload page after short delay to show updated schema
                setTimeout(function() {
                    location.reload();
                }, 1500);
            } else {
                var errorMessage = response.data || svpMetaboxData.i18n.unknownError;
                $status.html('<span class="svp-status-error">✗ ' + errorMessage + '</span>');
                $generateBtn.prop('disabled', false).text(svpMetaboxData.i18n.generateButton);
            }
        }

        /**
         * Handle error response with retry logic
         */
        function handleError(xhr, status, error, attemptNumber) {
            var statusCode = xhr.status || 0;
            var isRetryable = RETRY_CONFIG.retryableStatusCodes.indexOf(statusCode) !== -1;
            var canRetry = attemptNumber < RETRY_CONFIG.maxRetries && isRetryable;

            // Log error for debugging
            if (window.console && console.warn) {
                console.warn('Schema Validator Pro: AJAX error (attempt ' + (attemptNumber + 1) + ')', {
                    status: statusCode,
                    error: error,
                    retryable: isRetryable,
                    willRetry: canRetry
                });
            }

            if (canRetry) {
                // Calculate delay with exponential backoff
                var delay = Math.min(
                    RETRY_CONFIG.baseDelay * Math.pow(2, attemptNumber),
                    RETRY_CONFIG.maxDelay
                );

                // Add jitter (±25%)
                delay = delay * (0.75 + Math.random() * 0.5);

                // Show retry message
                $status.html(
                    '<span class="svp-status-warning">⚠ ' +
                    svpMetaboxData.i18n.retryingMessage +
                    ' ' + Math.round(delay / 1000) + 's...</span>'
                );

                // Retry after delay
                setTimeout(function() {
                    generateSchema(attemptNumber + 1);
                }, delay);
            } else {
                // No more retries or non-retryable error
                var errorMessage = svpMetaboxData.i18n.networkError;

                // Check if we have a detailed error message from the server
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    var detail = xhr.responseJSON.detail;
                    if (detail.message) {
                        errorMessage = detail.message;
                    }

                    // Show retry suggestion if available
                    if (detail.retryable && detail.retry_after) {
                        errorMessage += ' ' + svpMetaboxData.i18n.retryAfter.replace('%s', detail.retry_after);
                    }
                }

                $status.html('<span class="svp-status-error">✗ ' + errorMessage + '</span>');
                $generateBtn.prop('disabled', false).text(svpMetaboxData.i18n.generateButton);

                // Log final error
                if (window.console && console.error) {
                    console.error('Schema Validator Pro: Request failed after ' + (attemptNumber + 1) + ' attempts', {
                        status: statusCode,
                        error: error,
                        response: xhr.responseJSON
                    });
                }
            }
        }
    }

    // Initialize when document is ready
    $(document).ready(function() {
        initMetabox();
    });

})(jQuery);

