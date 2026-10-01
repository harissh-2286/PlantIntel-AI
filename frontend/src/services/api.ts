export interface Checks {
    format: boolean;
    resolution: boolean;
    blur: boolean;
    brightness: boolean;
    contrast: boolean;
}

export interface LeafDetection {
    status: string;
    message: string;
}

export interface QualityResponse {
    valid: boolean;
    quality_score: number;
    checks: Checks;
    warnings: string[];
    blur_score: number;
    blur_status: string;
    brightness_score: number;
    brightness_status: string;
    contrast_score: number;
    contrast_status: string;
    leaf_detection: LeafDetection;
}

export interface Prediction {
    class_id: number;
    class_name: string;
    confidence: number;
}

export interface PredictResponse {
    model: {
        name: string;
        architecture?: string;
        mode: string;
        version?: string;
    };
    prediction: Prediction;
    top_predictions: Prediction[];
    inference_time_ms?: number;
    confidence_warning?: string | null;
}

export interface SeverityInfo {
    percentage: number;
    level: string;
}

export interface SeverityArea {
    leaf_pixels: number;
    affected_pixels: number;
}

export interface SeverityResponse {
    status: string;
    severity_status?: string;
    message?: string;
    mode: string;
    severity: SeverityInfo;
    area: SeverityArea;
    visualization?: {
        overlay_base64: string;
        mask_label: string;
    } | null;
    severity_inference_time_ms?: number;
}

export interface AnalyzeFullResponse {
    quality: QualityResponse;
    model: {
        name: string;
        architecture: string;
        mode: string;
        version?: string;
    };
    prediction: Prediction;
    top_predictions: Prediction[];
    confidence_warning?: string | null;
    severity: SeverityInfo;
    area: SeverityArea;
    severity_status?: string;
    severity_message?: string;
    severity_visualization?: string | null;
    inference_time_ms?: number;
}

export interface ModelInfo {
    name: string;
    architecture?: string;
    framework: string;
    weights: string;
    num_classes: number;
    mode: string;
    version?: string;
    device: string;
    checkpoint?: string | null;
    total_parameters?: number;
    trainable_parameters?: number;
}

export interface AttentionResponse {
    model: string;
    version?: string;
    prediction: Prediction;
    attention: {
        has_attention: boolean;
        message?: string;
        channel_top_weights?: Array<{ channel_id: number; weight: number }>;
        spatial_map_dimensions?: number[];
        spatial_heatmap?: string | null;
    };
    inference_time_ms?: number;
}

export interface ExperimentMetrics {
    model_name: string;
    accuracy: number;
    precision_macro: number;
    recall_macro: number;
    f1_macro: number;
    total_parameters: number;
    inference_time_ms_per_image: number;
}

export interface ResearchMetricsResponse {
    status?: string;
    message?: string;
    accuracy?: number;
    macro_precision?: number;
    macro_recall?: number;
    macro_f1?: number;
    weighted_precision?: number;
    weighted_recall?: number;
    weighted_f1?: number;
    test_images?: number;
    checkpoint?: string;
    classification_report?: Record<string, any>;
    training_history?: {
        epochs: number[];
        train_loss: number[];
        val_loss: number[];
        train_accuracy: number[];
        val_accuracy: number[];
        learning_rate: number[];
    };
}

export interface ModelComparisonResponse {
    status?: string;
    message?: string;
    baseline?: ExperimentMetrics;
    attention?: ExperimentMetrics;
}

export interface AblationStudyResponse {
    status?: string;
    message?: string;
    experiments?: Record<string, ExperimentMetrics>;
}

export const checkImageQuality = async (file: File): Promise<QualityResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/quality-check', {
        method: 'POST',
        body: formData,
    });
    
    if (response.status === 413) {
        throw new Error("Image is too large. Maximum file size is 10 MB.");
    }
    
    if (!response.ok) {
        if (response.status === 400 || response.status === 422) {
             throw new Error("This image cannot be processed.");
        } else if (response.status >= 500) {
             throw new Error("Something went wrong while analyzing the image.");
        }
        throw new Error("Unable to connect to the analysis service.");
    }
    
    const data = await response.json();
    return data;
}

export const predictImage = async (file: File): Promise<PredictResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        if (response.status === 503) {
            throw new Error("Unable to load EfficientNetV2-S.");
        }
        throw new Error("Model inference failed.");
    }
    
    return await response.json();
}

export const analyzeSeverity = async (file: File): Promise<SeverityResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/severity', {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error("Severity estimation failed.");
    }
    
    return await response.json();
}

export const analyzeFullPipeline = async (file: File): Promise<AnalyzeFullResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        if (response.status === 503) {
            throw new Error("AI service is currently unavailable.");
        }
        throw new Error("Full pipeline analysis failed.");
    }
    
    return await response.json();
}

export const getAttentionMap = async (file: File): Promise<AttentionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/explain/attention', {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error("Failed to extract attention map.");
    }
    
    return await response.json();
}

export const getModelInfo = async (): Promise<ModelInfo> => {
    const response = await fetch('/api/model/info');
    if (!response.ok) {
        throw new Error("AI model dependencies are not installed.");
    }
    return await response.json();
}

export interface GradCAMExplanation {
    method: string;
    target_layer: string;
    target_class: number;
    original: string;
    original_base64: string;
    heatmap: string;
    heatmap_base64: string;
    overlay: string;
    overlay_base64: string;
    explanation_text: string;
}

export interface GradCAMResponse {
    model: {
        name: string;
        architecture?: string;
        mode: string;
        version?: string;
    };
    prediction: Prediction;
    top_predictions?: Prediction[];
    explanation: GradCAMExplanation;
    explanation_time_ms?: number;
}

export interface CombinedExplainResponse {
    model: {
        name: string;
        architecture?: string;
        mode: string;
        version?: string;
    };
    prediction: Prediction;
    top_predictions: Prediction[];
    attention: {
        has_attention: boolean;
        message?: string;
        channel_top_weights?: Array<{ channel_id: number; weight: number }>;
        spatial_map_dimensions?: number[];
        spatial_heatmap?: string | null;
    };
    gradcam: GradCAMExplanation;
    explanation_time_ms?: number;
}

export const getGradCAMExplanation = async (file: File, targetClass?: number): Promise<GradCAMResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (targetClass !== undefined && targetClass !== null) {
        formData.append('target_class', targetClass.toString());
    }
    
    const response = await fetch('/api/explain/gradcam', {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error("Unable to generate Grad-CAM++ explanation.");
    }
    
    return await response.json();
}

export const getCombinedExplanation = async (file: File, targetClass?: number): Promise<CombinedExplainResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (targetClass !== undefined && targetClass !== null) {
        formData.append('target_class', targetClass.toString());
    }
    
    const response = await fetch('/api/explain', {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error("Unable to generate combined explanation.");
    }
    
    return await response.json();
}

export const getResearchMetrics = async (): Promise<ResearchMetricsResponse> => {
    const response = await fetch('/api/research/metrics');
    if (!response.ok) {
        throw new Error("Failed to fetch research metrics.");
    }
    return await response.json();
}

export const getModelComparison = async (): Promise<ModelComparisonResponse> => {
    const response = await fetch('/api/research/comparison');
    if (!response.ok) {
        throw new Error("Failed to fetch model comparison data.");
    }
    return await response.json();
}

export const getAblationStudy = async (): Promise<AblationStudyResponse> => {
    const response = await fetch('/api/research/ablation');
    if (!response.ok) {
        throw new Error("Failed to fetch ablation study data.");
    }
    return await response.json();
}

export const getTrainingHistory = async (): Promise<{ baseline: any; attention: any }> => {
    const response = await fetch('/api/research/history');
    if (!response.ok) {
        throw new Error("Failed to fetch training history data.");
    }
    return await response.json();
}

export interface HistoryItem {
    analysis_id: string;
    created_at: string;
    predicted_class: string;
    predicted_class_id: number;
    confidence: number;
    severity_percentage: number;
    severity_level: string;
    analysis_status: string;
    image_url?: string | null;
}

export interface HistoryResponse {
    items: HistoryItem[];
    total: number;
    limit: number;
    offset: number;
}

export interface SingleAnalysisResponse {
    analysis_id: string;
    created_at: string;
    image_filename: string;
    image_url?: string | null;
    image_width?: number | null;
    image_height?: number | null;
    model: {
        name: string;
        version?: string | null;
        mode?: string | null;
    };
    prediction: Prediction;
    top_predictions?: Prediction[];
    severity: SeverityInfo;
    area: SeverityArea;
    visualizations?: {
        severity_overlay?: string | null;
        gradcam_overlay?: string | null;
    };
    analysis_status: string;
}

export interface HistoryStatsResponse {
    total_analyses: number;
    diseases_detected_count: number;
    average_severity_percentage: number;
    severity_distribution: Record<string, number>;
    disease_distribution: Record<string, number>;
}

export const getHistory = async (params: {
    limit?: number;
    offset?: number;
    search?: string;
    disease?: string;
    severity?: string;
    status?: string;
    sort_by?: string;
}): Promise<HistoryResponse> => {
    const query = new URLSearchParams();
    if (params.limit !== undefined) query.append("limit", params.limit.toString());
    if (params.offset !== undefined) query.append("offset", params.offset.toString());
    if (params.search) query.append("search", params.search);
    if (params.disease) query.append("disease", params.disease);
    if (params.severity) query.append("severity", params.severity);
    if (params.status) query.append("status", params.status);
    if (params.sort_by) query.append("sort_by", params.sort_by);

    const response = await fetch(`/api/history?${query.toString()}`);
    if (!response.ok) {
        throw new Error("Unable to load analysis history.");
    }
    return await response.json();
}

export const getSingleAnalysis = async (analysisId: string): Promise<SingleAnalysisResponse> => {
    const response = await fetch(`/api/history/${encodeURIComponent(analysisId)}`);
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error("Analysis record not found.");
        }
        throw new Error("Failed to load analysis record.");
    }
    return await response.json();
}

export const deleteAnalysis = async (analysisId: string): Promise<void> => {
    const response = await fetch(`/api/history/${encodeURIComponent(analysisId)}`, {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error("Failed to delete analysis record.");
    }
}

export const getHistoryStats = async (): Promise<HistoryStatsResponse> => {
    const response = await fetch('/api/history/stats');
    if (!response.ok) {
        throw new Error("Failed to load history statistics.");
    }
    return await response.json();
}



