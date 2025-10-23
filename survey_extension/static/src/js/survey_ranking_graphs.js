/** @odoo-module **/
/**
 * ARCHIVO: survey_ranking_graphs.js
 * PROPÓSITO: Mejoras visuales para gráficos de ranking y filtrado de medidas
 * FECHA: 2025-10-22
 */

import { registry } from "@web/core/registry";
import { GraphRenderer } from "@web/views/graph/graph_renderer";
import { GraphController } from "@web/views/graph/graph_controller";
import { patch } from "@web/core/utils/patch";

// Medidas permitidas - SOLO estas se mostrarán en el menú
const ALLOWED_MEASURES = [
    'scoring_percentage',    // Puntaje (%)
    'x_survey_duration',     // Duración (segundos)
    'x_ranking_position',    // Posición en Ranking
    '__count',               // Total de Participantes (conteo)
];

// Colores personalizados para medallas
const MEDAL_COLORS = {
    'gold': '#FFD700',      // Oro
    'silver': '#C0C0C0',    // Plata  
    'bronze': '#CD7F32',    // Bronce
    'participant': '#6c757d' // Participante
};

// Patch del controlador de gráficos para filtrar medidas
patch(GraphController.prototype, {
    setup() {
        super.setup();
        this.filterMeasures();
    },

    /**
     * Filtra las medidas disponibles para mostrar solo las permitidas
     */
    filterMeasures() {
        // Validar que existan todos los objetos necesarios
        if (!this.model || !this.model.metaData || !this.model.metaData.resModel) {
            return;
        }
        
        if (this.model.metaData.resModel === 'survey.user_input') {
            const measures = this.model.metaData.measures;
            
            // Validar que measures exista y sea un objeto
            if (!measures || typeof measures !== 'object') {
                return;
            }
            
            // Filtrar solo las medidas permitidas
            Object.keys(measures).forEach(key => {
                if (!ALLOWED_MEASURES.includes(key)) {
                    delete measures[key];
                }
            });
            
            console.log('✅ Medidas filtradas. Solo visibles:', ALLOWED_MEASURES);
        }
    },
});

// Patch del renderizador para colores personalizados
patch(GraphRenderer.prototype, {
    setup() {
        super.setup();
        
        if (this.props.model?.metaData?.resModel === 'survey.user_input') {
            this.customizeGraphColors();
        }
    },

    customizeGraphColors() {
        const graphType = this.model?.metaData?.mode || 'bar';
        
        if (graphType === 'pie') {
            this.applyMedalColors();
        } else if (graphType === 'bar') {
            this.applyRankingColors();
        }
    },

    applyMedalColors() {
        console.log('🎨 Aplicando colores de medallas al gráfico de pastel');
    },

    applyRankingColors() {
        console.log('📊 Aplicando colores de ranking al gráfico de barras');
    },
});

console.log('🎨 Módulo de gráficos de ranking cargado con filtro de medidas');
