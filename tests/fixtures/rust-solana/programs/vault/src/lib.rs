//! Seeded vulnerable Solana-style program for the Phase A eval.
//! One deliberate instance of each rule family:
//!   - missing signer check   (withdraw_sol, line ~20)
//!   - missing ownership check (set_admin / transfer_ownership path)
//!   - unchecked arithmetic    (donate -> balance math)
//! plus one CLEAN function that must NOT be flagged (false-positive guard).

use anchor_lang::prelude::*;
use solana_program::{msg, system_instruction};

declare_id!("Kw4roSeed11111111111111111111111111111111111");

#[program]
pub mod vault {
    use super::*;

    /// VULN 1 (missing signer check): authority account is never verified
    /// with `is_signer` or `require!` before lamports move out.
    pub fn withdraw_sol(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        let vault = &ctx.accounts.vault;
        let dest = &ctx.accounts.destination;
        **vault.try_borrow_mut_lamports()? -= amount;
        **dest.try_borrow_mut_lamports()? += amount;
        Ok(())
    }

    /// VULN 2 (missing ownership check): anyone can point `admin` at their own
    /// wallet; the handler never compares admin.key to the stored owner.
    pub fn set_config(ctx: Context<SetConfig>, fee_bps: u16) -> Result<()> {
        let admin = &ctx.accounts.admin;
        let cfg = &mut ctx.accounts.config;
        cfg.fee_bps = fee_bps;
        cfg.authority = admin.key();
        emit!(ConfigChanged { fee_bps });
        Ok(())
    }

    /// VULN 3 (unchecked arithmetic): raw `-`/`+` on balances can underflow.
    pub fn donate(ctx: Context<Donate>, amount: u64) -> Result<()> {
        let pot = &mut ctx.accounts.pot;
        pot.balance = pot.balance - amount + amount;
        msg!("donated");
        Ok(())
    }

    /// CLEAN: proper signer + ownership checks and checked arithmetic.
    /// Must NOT be reported by any Phase A rule.
    pub fn withdraw_checked(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        let w = &ctx.accounts;
        require_keys_eq!(w.authority.key(), w.vault.owner);
        require!(w.authority.is_signer, VaultError::NotSigner);
        let new_amt = w
            .vault
            .lamports()
            .checked_sub(amount)
            .ok_or(VaultError::Overflow)?;
        **w.vault.try_borrow_mut_lamports()? = new_amt;
        Ok(())
    }
}

#[error_code]
pub enum VaultError {
    NotSigner,
    Overflow,
}

#[event]
pub struct ConfigChanged {
    pub fee_bps: u16,
}
