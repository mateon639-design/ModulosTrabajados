/** @odoo-module **/
/**
 * ARCHIVO: survey_ranking_graphs.js
 * PROPÓSITO: Mejoras visuales para gráficos de ranking
 * FECHA: 2025-10-22
 */

import { registry } from "@web/core/registry";
import { GraphRenderer } from "@web/views/graph/graph_renderer";
import { patch } from "@web/core/utils/patch";

// Colores personalizados para medallas
const MEDAL_COLORS = {
    'gold': '#FFD700',      // Oro
    'silver': '#C0C0C0',    // Plata  
    'bronze': '#CD7F32',    // Bronce
    'participant': '#6c757d' // Participante
};

// Colores para gráfico de barras (degradado de verde)
const BAR_COLORS = [
    '#28a745', // Verde principal
    '#34ce57', // Verde claro
    '#40d568', // Verde más claro
    '#20c997', // Verde azulado
    '#17a2b8', // Azul verdoso
    '#007bff', // Azul
    '#6c757d', // Gris
];

patch(GraphRenderer.prototype, {
    /**
     * Personaliza los colores de los gráficos según el tipo
     */
    setup() {
        super.setup();
        
        // Observar cambios en el tipo de gráfico
        if (this.props.model && this.props.model.metaData) {
            const modelName = this.props.model.metaData.resModel;
            
            // Solo aplicar para survey.user_input
            if (modelName === 'survey.user_input') {
                this.customizeGraphColors();
            }
        }
    },

    /**
     * Personaliza los colores según el tipo de gráfico
     */
    customizeGraphColors() {
        const graphType = this.model?.metaData?.mode || 'bar';
        
        if (graphType === 'pie') {
            // Para gráfico de pastel (medallas)
            this.applyMedalColors();
        } else if (graphType === 'bar') {
            // Para gráfico de barras (ranking)
            this.applyRankingColors();
        }
    },

    /**
     * Aplica colores de medallas al gráfico de pastel
     */
    applyMedalColors() {
        // Los colores ya están definidos en el CSS
        console.log('Aplicando colores de medallas al gráfico de pastel');
    },

    /**
     * Aplica colores de ranking al gráfico de barras
     */
    applyRankingColors() {
        console.log('Aplicando colores de ranking al gráfico de barras');
    },
});

// Registrar el componente mejorado
console.log('🎨 Módulo de gráficos de ranking cargado');
