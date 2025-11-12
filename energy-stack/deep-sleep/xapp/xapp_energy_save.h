/*
 * FlexRIC Energy Saving xApp Header
 * xapp_energy_save.h
 */

#ifndef XAPP_ENERGY_SAVE_H
#define XAPP_ENERGY_SAVE_H

#include "../../src/xApp/e42_xapp_api.h"
#include "../../src/sm/mac_sm/mac_sm_id.h"
#include "../../src/sm/mac_sm/ie/mac_data_ie.h"
#include "../../src/util/time_now_us.h"

#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

// xApp Configuration
#define XAPP_NAME "EnergyStatsApplication"
#define XAPP_VERSION "1.0.0"

// Energy saving parameters
#define PDSCH_TIMEOUT_MS 500
#define PDSCH_TIMEOUT_US (PDSCH_TIMEOUT_MS * 1000)
#define MAX_HARQ_FAILURES 0
#define TTI_DURATION_US 1000
#define ENERGY_REDUCTION_PERCENT 37

// MAC RAN Function ID
#define MAC_RAN_FUNC_ID 26

// Energy state structure
typedef struct {
    bool tx_active;
    uint64_t last_pdsch_time;
    uint64_t no_pdsch_start_time;
    uint32_t harq_failure_count;
    bool deep_sleep_active;
    uint32_t energy_save_cycles;
} energy_save_state_t;

// xApp context structure
typedef struct {
    e2_node_arr_t nodes;
    energy_save_state_t energy_state;
} xapp_energy_ctx_t;

// Function declarations
static void mac_stats_handle(e2_node_t const* node, mac_ind_msg_t const* ind_msg);
static void toggle_transmit_chain(e2_node_t const* node, bool enable);
static void check_energy_save_conditions(e2_node_t const* node);
static void e2_setup_req_handle(e2_setup_req_t const* sr);
static void e2_node_conn_handle(e2_node_t const* node);
static void e2_node_disconn_handle(e2_node_t const* node);

#endif // XAPP_ENERGY_SAVE_H