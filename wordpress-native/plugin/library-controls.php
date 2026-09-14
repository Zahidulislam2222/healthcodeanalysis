<?php
/** Native functional widget for controls absent from Elementor Free's core widgets. */
if ( ! defined( 'ABSPATH' ) ) { exit; }
add_action( 'elementor/widgets/register', function ( $manager ) {
    class HCN_Library_Controls extends \Elementor\Widget_Base {
        public function get_name() { return 'hcn-library-controls'; }
        public function get_title() { return 'HealthCode library filters'; }
        public function get_icon() { return 'eicon-search'; }
        public function get_categories() { return array( 'general' ); }
        protected function register_controls() {
            $this->start_controls_section( 'content', array( 'label' => 'Library filters' ) );
            $this->add_control( 'search_label', array( 'label' => 'Search label', 'type' => \Elementor\Controls_Manager::TEXT ) );
            $this->add_control( 'topic_label', array( 'label' => 'Topic label', 'type' => \Elementor\Controls_Manager::TEXT ) );
            $this->add_control( 'all_label', array( 'label' => 'All topics label', 'type' => \Elementor\Controls_Manager::TEXT ) );
            $this->add_control( 'categories', array( 'label' => 'Categories, one per line', 'type' => \Elementor\Controls_Manager::TEXTAREA ) );
            $this->add_control( 'initial_count', array( 'label' => 'Initial count', 'type' => \Elementor\Controls_Manager::NUMBER ) );
            $this->add_control( 'clear_label', array( 'label' => 'Clear saved list label (empty hides control)', 'type' => \Elementor\Controls_Manager::TEXT ) );
            $this->end_controls_section();
        }
        protected function render() {
            $s = $this->get_settings_for_display();
            echo '<div class="filter-bar"><label class="search-field"><input type="search" data-filter-search aria-label="' . esc_attr( $s['search_label'] ) . '" placeholder="' . esc_attr( $s['search_label'] ) . '"></label>';
            echo '<label class="topic-select"><span>' . esc_html( $s['topic_label'] ) . '</span><select data-filter-category><option value="">' . esc_html( $s['all_label'] ) . '</option>';
            foreach ( explode( "\n", $s['categories'] ) as $category ) {
                $category = trim( $category );
                if ( $category ) { echo '<option>' . esc_html( $category ) . '</option>'; }
            }
            echo '</select></label>';
            if ( $s['clear_label'] ) { echo '<button type="button" class="text-link" data-clear-saved>' . esc_html( $s['clear_label'] ) . '</button>'; }
            echo '<span class="result-count" aria-live="polite"><span data-result-count>' . (int) $s['initial_count'] . '</span> ' . esc_html( hcn_data( 'site' )['labels']['results'] ) . '</span></div>';
        }
    }
    $manager->register( new HCN_Library_Controls() );
} );
