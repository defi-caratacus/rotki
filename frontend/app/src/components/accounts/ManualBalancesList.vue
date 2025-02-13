<template>
  <div>
    <v-row no-gutters justify="end">
      <v-col cols="12" sm="6" class="d-flex flex-row align-center">
        <tag-filter v-model="onlyTags" />
      </v-col>
    </v-row>
    <v-sheet outlined rounded>
      <data-table
        :loading="loading"
        :headers="headers"
        :items="visibleBalances"
        class="manual-balances-list"
        sort-by="usdValue"
      >
        <template #item.label="{ item }">
          <v-row>
            <v-col
              cols="12"
              class="font-weight-medium manual-balances-list__label"
              :class="!item.tags ? 'pt-0' : ''"
            >
              {{ item.label }}
            </v-col>
          </v-row>
          <v-row v-if="item.tags">
            <v-col cols="12">
              <tag-icon
                v-for="tag in item.tags"
                :key="tag"
                class="manual-balances-list__tag"
                :tag="tags[tag]"
              />
            </v-col>
          </v-row>
        </template>
        <template #header.usdValue>
          {{
            $t('manual_balances_list.headers.value', {
              symbol
            })
          }}
        </template>
        <template #item.asset="{ item }">
          <asset-details opens-details :asset="item.asset" />
        </template>
        <template #item.amount="{ item }">
          <amount-display
            class="manual-balances-list__amount"
            :value="item.amount"
          />
        </template>
        <template #item.usdValue="{ item }">
          <amount-display
            show-currency="symbol"
            :amount="item.amount"
            :fiat-currency="item.asset"
            :value="item.usdValue"
          />
        </template>
        <template #item.location="{ item }">
          <location-display
            class="manual-balances-list__location"
            :identifier="item.location"
          />
        </template>
        <template #item.actions="{ item }">
          <span>
            <v-icon
              small
              class="mr-2 manual-balances-list__actions__edit"
              @click="editBalance(item)"
            >
              mdi-pencil
            </v-icon>
            <v-icon
              small
              class="manual-balances-list__actions__delete"
              @click="labelToDelete = item.label"
            >
              mdi-delete
            </v-icon>
          </span>
        </template>
        <template v-if="visibleBalances.length > 0" #body.append>
          <tr class="manual-balances-list__total">
            <td v-text="$t('manual_balances_list.total')" />
            <td />
            <td />
            <td class="text-end">
              <amount-display
                show-currency="symbol"
                class="manual-balances-list__amount"
                :fiat-currency="currency.ticker_symbol"
                :value="
                  visibleBalances
                    | aggregateTotal(
                      currency.ticker_symbol,
                      exchangeRate(currency.ticker_symbol),
                      floatingPrecision
                    )
                "
              />
            </td>
          </tr>
        </template>
      </data-table>
    </v-sheet>
    <confirm-dialog
      v-if="labelToDelete !== null"
      display
      :title="$t('manual_balances_list.delete_dialog.title')"
      :message="$t('manual_balances_list.delete_dialog.message')"
      @cancel="labelToDelete = null"
      @confirm="deleteLabel()"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import { DataTableHeader } from 'vuetify';
import { mapGetters, mapState } from 'vuex';
import ConfirmDialog from '@/components/dialogs/ConfirmDialog.vue';
import AmountDisplay from '@/components/display/AmountDisplay.vue';
import AssetDetails from '@/components/helper/AssetDetails.vue';
import DataTable from '@/components/helper/DataTable.vue';
import RefreshButton from '@/components/helper/RefreshButton.vue';
import TagFilter from '@/components/inputs/TagFilter.vue';
import TagIcon from '@/components/tags/TagIcon.vue';
import { CURRENCY_USD } from '@/data/currencies';
import { Currency } from '@/model/currency';
import {
  ManualBalance,
  ManualBalanceWithValue
} from '@/services/balances/types';
import { ExchangeRateGetter } from '@/store/balances/types';
import { Tags } from '@/typing/types';

@Component({
  components: {
    DataTable,
    RefreshButton,
    AmountDisplay,
    AssetDetails,
    ConfirmDialog,
    TagIcon,
    TagFilter
  },
  computed: {
    ...mapState('balances', ['manualBalances']),
    ...mapState('session', ['tags']),
    ...mapGetters('session', ['floatingPrecision', 'currency']),
    ...mapGetters('balances', ['exchangeRate'])
  }
})
export default class ManualBalancesList extends Vue {
  labelToDelete: string | null = null;
  onlyTags: string[] = [];
  edited: ManualBalance | null = null;

  get symbol(): string {
    return this.currency.ticker_symbol;
  }

  readonly headers: DataTableHeader[] = [
    {
      text: this.$t('manual_balances_list.headers.location').toString(),
      value: 'location',
      align: 'center',
      width: '120px'
    },
    {
      text: this.$t('manual_balances_list.headers.label').toString(),
      value: 'label'
    },
    {
      text: this.$t('manual_balances_list.headers.asset').toString(),
      value: 'asset',
      width: '200'
    },
    {
      text: this.$t('manual_balances_list.headers.amount').toString(),
      value: 'amount',
      align: 'end'
    },
    {
      text: this.$t('manual_balances_list.headers.value', {
        symbol: CURRENCY_USD
      }).toString(),
      value: 'usdValue',
      align: 'end'
    },
    {
      text: this.$t('manual_balances_list.headers.actions').toString(),
      value: 'actions',
      sortable: false,
      width: '50'
    }
  ];

  manualBalances!: ManualBalanceWithValue[];
  tags!: Tags;
  currency!: Currency;
  floatingPrecision!: number;
  exchangeRate!: ExchangeRateGetter;

  @Prop({ required: false, type: Boolean, default: false })
  loading: boolean = false;

  get visibleBalances(): ManualBalance[] {
    if (this.onlyTags.length === 0) {
      return this.manualBalances;
    }

    return this.manualBalances.filter(balance => {
      if (balance.tags) {
        return this.onlyTags.every(tag => balance.tags.includes(tag));
      }
    });
  }

  editBalance(balance: ManualBalance) {
    this.$emit('editBalance', balance);
  }

  async deleteLabel() {
    this.edited = null;
    await this.$store.dispatch(
      'balances/deleteManualBalance',
      this.labelToDelete
    );
    this.labelToDelete = null;
  }
}
</script>

<style scoped lang="scss">
.manual-balances-list {
  &__tag {
    margin-right: 8px;
  }

  &__total {
    font-weight: 500;
  }

  &__label {
    padding-bottom: 0 !important;
  }
}

::v-deep {
  th {
    &:first-child {
      span {
        padding-left: 16px;
      }
    }
  }
}
</style>
