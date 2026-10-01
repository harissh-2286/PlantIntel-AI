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

const DEFAULT_BACKEND = 'https://plantintel-ai.onrender.com';
export const API_BASE_URL = (import.meta.env.VITE_API_URL || (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app') ? DEFAULT_BACKEND : '')).replace(/\/$/, '');

async function fetchApi<T>(endpoint: string, options?: RequestInit, defaultErrorMessage?: string): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    let response: Response;
    try {
        response = await fetch(url, options);
    } catch (err: any) {
        throw new Error(`Unable to connect to backend server. ${err?.message || ''}`);
    }

    const contentType = response.headers.get('content-type') || '';

    if (contentType.includes('text/html')) {
        throw new Error("Backend API server returned HTML instead of JSON. Ensure your Python backend is running and VITE_API_URL is configured.");
    }

    const text = await response.text();

    if (text.trim().startsWith('<')) {
        throw new Error("Backend API endpoint returned an HTML page (404/Route Mismatch). Please set VITE_API_URL in your environment.");
    }

    if (!response.ok) {
        let errorMsg = '';
        try {
            const errorJson = JSON.parse(text);
            if (errorJson.detail) {
                errorMsg = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
            } else if (errorJson.message) {
                errorMsg = errorJson.message;
            }
        } catch {
            // Not JSON
        }

        if (response.status === 413) {
            throw new Error("Image is too large. Maximum file size is 10 MB.");
        } else if (response.status === 503) {
            throw new Error(errorMsg || defaultErrorMessage || "AI service is currently unavailable.");
        } else if (response.status === 404) {
            throw new Error(errorMsg || defaultErrorMessage || "Requested resource not found.");
        } else if (response.status === 400 || response.status === 422) {
            throw new Error(errorMsg || defaultErrorMessage || "This image cannot be processed.");
        } else if (response.status >= 500) {
            throw new Error(errorMsg || defaultErrorMessage || "Something went wrong on the backend server.");
        }

        throw new Error(errorMsg || defaultErrorMessage || `Server error (${response.status})`);
    }

    if (!text || text.trim() === '') {
        return {} as T;
    }

    try {
        return JSON.parse(text) as T;
    } catch {
        throw new Error("Invalid JSON response received from backend API server.");
    }
}

export const checkImageQuality = async (file: File): Promise<QualityResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetchApi<QualityResponse>('/api/quality-check', {
        method: 'POST',
        body: formData,
    }, "Unable to connect to the analysis service.");
}

export const predictImage = async (file: File): Promise<PredictResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetchApi<PredictResponse>('/api/predict', {
        method: 'POST',
        body: formData,
    }, "Model inference failed.");
}

export const analyzeSeverity = async (file: File): Promise<SeverityResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetchApi<SeverityResponse>('/api/severity', {
        method: 'POST',
        body: formData,
    }, "Severity estimation failed.");
}

export const analyzeFullPipeline = async (file: File): Promise<AnalyzeFullResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetchApi<AnalyzeFullResponse>('/api/analyze', {
        method: 'POST',
        body: formData,
    }, "Full pipeline analysis failed.");
}

export const getAttentionMap = async (file: File): Promise<AttentionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetchApi<AttentionResponse>('/api/explain/attention', {
        method: 'POST',
        body: formData,
    }, "Failed to extract attention map.");
}

export const getModelInfo = async (): Promise<ModelInfo> => {
    return fetchApi<ModelInfo>('/api/model/info', undefined, "AI model dependencies are not installed.");
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
    
    return fetchApi<GradCAMResponse>('/api/explain/gradcam', {
        method: 'POST',
        body: formData,
    }, "Unable to generate Grad-CAM++ explanation.");
}

export const getCombinedExplanation = async (file: File, targetClass?: number): Promise<CombinedExplainResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (targetClass !== undefined && targetClass !== null) {
        formData.append('target_class', targetClass.toString());
    }
    
    return fetchApi<CombinedExplainResponse>('/api/explain', {
        method: 'POST',
        body: formData,
    }, "Unable to generate combined explanation.");
}

export const getResearchMetrics = async (): Promise<ResearchMetricsResponse> => {
    return fetchApi<ResearchMetricsResponse>('/api/research/metrics', undefined, "Failed to fetch research metrics.");
}

export const getModelComparison = async (): Promise<ModelComparisonResponse> => {
    return fetchApi<ModelComparisonResponse>('/api/research/comparison', undefined, "Failed to fetch model comparison data.");
}

export const getAblationStudy = async (): Promise<AblationStudyResponse> => {
    return fetchApi<AblationStudyResponse>('/api/research/ablation', undefined, "Failed to fetch ablation study data.");
}

export const getTrainingHistory = async (): Promise<{ baseline: any; attention: any }> => {
    return fetchApi<{ baseline: any; attention: any }>('/api/research/history', undefined, "Failed to fetch training history data.");
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

    return fetchApi<HistoryResponse>(`/api/history?${query.toString()}`, undefined, "Unable to load analysis history.");
}

export const getSingleAnalysis = async (analysisId: string): Promise<SingleAnalysisResponse> => {
    return fetchApi<SingleAnalysisResponse>(`/api/history/${encodeURIComponent(analysisId)}`, undefined, "Failed to load analysis record.");
}

export const deleteAnalysis = async (analysisId: string): Promise<void> => {
    return fetchApi<void>(`/api/history/${encodeURIComponent(analysisId)}`, {
        method: 'DELETE'
    }, "Failed to delete analysis record.");
}

export const getHistoryStats = async (): Promise<HistoryStatsResponse> => {
    return fetchApi<HistoryStatsResponse>('/api/history/stats', undefined, "Failed to load history statistics.");
}

// ─────────────────────────────────────────────────────────────────────
// Phase 12 — Plant Health Guidance & Continuous Monitoring API
// ─────────────────────────────────────────────────────────────────────

export interface GuidanceSource {
    source_type: string;
    source_title: string;
    source_url: string;
    source_date?: string;
}

export interface RecommendationCard {
    id: string;
    title: string;
    description: string;
    why_it_matters: string;
    priority: string;
    applicable_condition: string;
    source?: GuidanceSource;
}

export interface GuidanceResponse {
    analysis_id: string;
    knowledge_base_version: string;
    crop: string;
    growth_stage: string;
    environment: string;
    predicted_class: string;
    confidence: number;
    confidence_level: string;
    is_confirmed: boolean;
    status_label: string;
    health_status: string;
    health_indicator_score: number;
    severity_percentage: number;
    severity_level: string;
    severity_interpretation: string;
    immediate_actions: RecommendationCard[];
    prevention: RecommendationCard[];
    water_and_environment: RecommendationCard[];
    nutrition_guidance: RecommendationCard[];
    natural_and_biological_options: RecommendationCard[];
    what_to_avoid: RecommendationCard[];
    disease_vs_nutrient_note: string;
    chemical_management_reference?: string;
    resistance_management_note?: string;
    integrated_pest_management_note: string;
    monitoring_interval_days: number;
    recommended_next_check: string;
    when_to_seek_expert_advice: string[];
    sources: GuidanceSource[];
    disclaimer: string;
}

export interface GuidanceRequest {
    analysis_id: string;
    crop?: string | null;
    variety?: string | null;
    growth_stage?: string;
    environment?: string;
    soil_type?: string | null;
    irrigation_method?: string | null;
}

export const getPlantGuidance = async (req: GuidanceRequest): Promise<GuidanceResponse> => {
    return fetchApi<GuidanceResponse>('/api/guidance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
    }, "Failed to generate plant health guidance.");
}

export const getSupportedCrops = async () => {
    return fetchApi<{ knowledge_base_version: string; supported_crops: any[]; note: string }>(
        '/api/guidance/crops', undefined, "Failed to fetch supported crops."
    );
}

export const getSupportedDiseases = async () => {
    return fetchApi<{ knowledge_base_version: string; total_diseases: number; diseases: any[] }>(
        '/api/guidance/diseases', undefined, "Failed to fetch supported diseases."
    );
}

// Plant Profile / Monitoring APIs

export interface PlantItem {
    plant_id: string;
    name: string;
    crop: string;
    variety?: string;
    created_at: string;
    last_scan_at?: string;
    health_status: string;
    latest_disease?: string;
    latest_confidence?: number;
    latest_severity?: number;
    analysis_count: number;
}

export interface PlantCreateRequest {
    name: string;
    crop: string;
    variety?: string;
    growth_stage?: string;
    environment?: string;
    soil_type?: string;
    irrigation_method?: string;
    location?: string;
    notes?: string;
    initial_analysis_id?: string;
}

export const createPlant = async (req: PlantCreateRequest): Promise<PlantItem> => {
    return fetchApi<PlantItem>('/api/plants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
    }, "Failed to create plant profile.");
}

export const getPlants = async (limit = 100, offset = 0) => {
    return fetchApi<{ plants: PlantItem[]; total: number; limit: number; offset: number }>(
        `/api/plants?limit=${limit}&offset=${offset}`, undefined, "Failed to fetch plant profiles."
    );
}

export const getPlantDetail = async (plantId: string) => {
    return fetchApi<any>(`/api/plants/${encodeURIComponent(plantId)}`, undefined, "Failed to fetch plant detail.");
}

export const linkAnalysisToPlant = async (plantId: string, analysisId: string, notes?: string) => {
    return fetchApi<any>(`/api/plants/${encodeURIComponent(plantId)}/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_id: analysisId, notes: notes || null }),
    }, "Failed to link analysis to plant.");
}

export const getPlantTimeline = async (plantId: string) => {
    return fetchApi<any>(`/api/plants/${encodeURIComponent(plantId)}/timeline`, undefined, "Failed to fetch plant timeline.");
}

export const getPlantTrend = async (plantId: string) => {
    return fetchApi<any>(`/api/plants/${encodeURIComponent(plantId)}/trend`, undefined, "Failed to fetch plant trend.");
}

export const getMonitoringDashboard = async () => {
    return fetchApi<any>('/api/plants/dashboard', undefined, "Failed to fetch monitoring dashboard.");
}

export const deletePlant = async (plantId: string): Promise<void> => {
    return fetchApi<void>(`/api/plants/${encodeURIComponent(plantId)}`, {
        method: 'DELETE',
    }, "Failed to delete plant profile.");
}
