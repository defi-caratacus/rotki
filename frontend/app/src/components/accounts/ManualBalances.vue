<template>
  <div>
    <v-card class="manual-balances mt-8">
      <v-card-title>
        <refresh-button
          :loading="loading"
          :tooltip="$t('manual_balances_list.refresh.tooltip')"
          @refresh="refresh()"
        />
        <card-title class="ms-2">{{ $t('manual_balances.title') }}</card-title>
      </v-card-title>
      <v-card-text>
        <v-btn
          absolute
          fab
          top
          right
          dark
          color="primary"
          class="manual-balances__add-balance"
          @click="newBalance()"
        >
          <v-icon> mdi-plus </v-icon>
        </v-btn>
        <big-dialog
          :display="openDialog"
          :title="dialogTitle"
          :subtitle="dialogSubtitle"
          :action-disabled="dialogDisabled || !valid || dialogLoading"
          :loading="dialogLoading"
          primary-action="Save"
          @confirm="save()"
          @cancel="cancel()"
        >
          <manual-balances-form
            ref="dialogChild"
            v-model="valid"
            :edit="balanceToEdit"
          />
        </big-dialog>
        <manual-balances-list :loading="loading" @editBalance="edit($event)" />
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { mapActions } from 'vuex';
import ManualBalancesForm from '@/components/accounts/ManualBalancesForm.vue';
import ManualBalancesList from '@/components/accounts/ManualBalancesList.vue';
import BigDialog from '@/components/dialogs/BigDialog.vue';
import RefreshButton from '@/components/helper/RefreshButton.vue';
import CardTitle from '@/components/typography/CardTitle.vue';
import { ManualBalance } from '@/services/balances/types';

@Component({
  components: {
    RefreshButton,
    CardTitle,
    ManualBalancesList,
    ManualBalancesForm,
    BigDialog
  },
  methods: {
    ...mapActions('balances', ['fetchManualBalances'])
  }
})
export default class ManualBalances extends Vue {
  balanceToEdit: ManualBalance | null = null;
  dialogTitle: string = '';
  dialogSubtitle: string = '';
  openDialog: boolean = false;
  dialogDisabled: boolean = false;
  dialogLoading: boolean = false;
  valid: boolean = false;
  loading: boolean = false;

  fetchManualBalances!: () => Promise<void>;

  newBalance() {
    this.dialogTitle = 'Add Manual Balance';
    this.dialogSubtitle = '';
    this.openDialog = true;
  }

  edit(balance: ManualBalance) {
    this.balanceToEdit = balance;
    this.dialogTitle = 'Edit Manual Balance';
    this.dialogSubtitle = 'Modify balance amount, location, and tags';
    this.openDialog = true;
  }

  async refresh() {
    this.loading = true;
    await this.fetchManualBalances();
    this.loading = false;
  }

  async save() {
    this.dialogDisabled = true;
    this.dialogLoading = true;
    const form = this.$refs.dialogChild as ManualBalancesForm;
    const success = await form.save();
    this.dialogDisabled = false;
    this.dialogLoading = false;

    if (!success) {
      return;
    }
    this.openDialog = false;
    this.balanceToEdit = null;
  }

  cancel() {
    this.openDialog = false;
    this.balanceToEdit = null;
  }

  mounted() {
    this.openDialog = !!this.$route.query.add;
  }
}
</script>

<style scoped></style>
