import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_typography.dart';
import '../models/credential.dart';
import 'status_badge.dart';
import 'kavach_card.dart';

class CredentialTile extends StatelessWidget {
  final CredentialModel credential;
  final VoidCallback onTap;

  const CredentialTile({
    super.key,
    required this.credential,
    required this.onTap,
  });

  IconData _categoryIcon(String category) {
    switch (category.toUpperCase()) {
      case 'IDENTITY':
        return Icons.badge_outlined;
      case 'KYC':
        return Icons.verified_user_outlined;
      case 'INCOME':
        return Icons.account_balance_wallet_outlined;
      default:
        return Icons.security_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    return KavachCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: AppColors.brandTint,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _categoryIcon(credential.category),
                  color: AppColors.brandGreen,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      credential.title,
                      style: AppTypography.titleMedium.copyWith(fontSize: 16),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      credential.issuer,
                      style: AppTypography.caption,
                    ),
                  ],
                ),
              ),
              StatusBadge(
                label: credential.status,
                type: credential.status == 'VALID' ? BadgeType.success : BadgeType.warning,
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('CREDENTIAL ID', style: AppTypography.caption),
                  const SizedBox(height: 2),
                  Text(
                    credential.id,
                    style: AppTypography.labelMedium.copyWith(
                      color: AppColors.textPrimary,
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('EXPIRY DATE', style: AppTypography.caption),
                  const SizedBox(height: 2),
                  Text(
                    credential.expiryDate,
                    style: AppTypography.labelMedium.copyWith(color: AppColors.textPrimary),
                  ),
                ],
              ),
            ],
          ),
          if (credential.isSynthetic) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.cardSubtle,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.info_outline, size: 12, color: AppColors.textSecondary),
                  const SizedBox(width: 6),
                  Text(
                    'Synthetic Demo Credential • Non-Governmental',
                    style: AppTypography.caption.copyWith(color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

