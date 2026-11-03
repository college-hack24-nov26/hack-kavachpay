import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/vault_provider.dart';
import '../../widgets/kavach_card.dart';
import '../../widgets/status_badge.dart';

class CredentialDetailScreen extends ConsumerWidget {
  final String credentialId;

  const CredentialDetailScreen({
    super.key,
    required this.credentialId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(credentialDetailProvider(credentialId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Credential Detail'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/vault');
            }
          },
        ),
      ),
      body: detailAsync.when(
        data: (cred) => SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Card
              KavachCard(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.brandTint,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            cred.category,
                            style: AppTypography.caption.copyWith(
                              color: AppColors.brandGreen,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        StatusBadge(
                          label: cred.status,
                          type: cred.status == 'VALID' ? BadgeType.success : BadgeType.warning,
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    Text(cred.title, style: AppTypography.titleLarge),
                    const SizedBox(height: 4),
                    Text(
                      'Issued by ${cred.issuer}',
                      style: AppTypography.bodyMedium,
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 16),

                    _attributeRow('Credential ID', cred.id, isMonospace: true),
                    const SizedBox(height: 10),
                    _attributeRow('Issue Date', cred.issueDate),
                    const SizedBox(height: 10),
                    _attributeRow('Expiry Date', cred.expiryDate),
                    const SizedBox(height: 10),
                    _attributeRow('Issuance Protocol', 'Ghost-Vault Decoupled v1.0'),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Synthetic Demo Notice (Mandatory Fintech Safety Disclosure)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.warningBg,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.warning.withOpacity(0.3)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: AppColors.warning, size: 22),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Synthetic Demo Credential',
                            style: AppTypography.labelLarge.copyWith(color: AppColors.warning),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'This credential contains synthetic test data generated for evaluation. It is NOT issued by a government authority or commercial bank.',
                            style: AppTypography.caption.copyWith(color: AppColors.textPrimary),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Safe Decoupled Attributes (Privacy-First)
              Text('Privacy-Preserving Attributes', style: AppTypography.titleMedium),
              const SizedBox(height: 4),
              Text(
                'These verified predicates can be proven to verifiers without sharing underlying sensitive identity or banking documents.',
                style: AppTypography.bodyMedium,
              ),
              const SizedBox(height: 12),

              if (cred.safeAttributes != null && cred.safeAttributes!.isNotEmpty) ...[
                KavachCard(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: cred.safeAttributes!.entries.map((entry) {
                      final label = entry.key
                          .replaceAll('_', ' ')
                          .split(' ')
                          .map((w) => w.isNotEmpty ? '${w[0].toUpperCase()}${w.substring(1)}' : '')
                          .join(' ');
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(label, style: AppTypography.bodyMedium),
                            Flexible(
                              child: Text(
                                '${entry.value}',
                                textAlign: TextAlign.right,
                                style: AppTypography.labelLarge.copyWith(
                                  color: AppColors.brandGreen,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],

              const SizedBox(height: 18),

              // Cryptographic Integrity Fingerprint
              Text('Cryptographic Integrity', style: AppTypography.titleMedium),
              const SizedBox(height: 8),
              KavachCard(
                backgroundColor: AppColors.cardSubtle,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(Icons.fingerprint, size: 20, color: AppColors.textSecondary),
                        SizedBox(width: 8),
                        Text('SHA-256 Digest Signature', style: AppTypography.labelMedium),
                      ],
                    ),
                    const SizedBox(height: 8),
                    SelectableText(
                      cred.verificationHash ?? 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                      style: AppTypography.caption.copyWith(
                        fontFamily: 'monospace',
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator(color: AppColors.brandGreen)),
        error: (err, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: KavachCard(
              child: Text('Failed to load credential detail: $err'),
            ),
          ),
        ),
      ),
    );
  }

  Widget _attributeRow(String label, String value, {bool isMonospace = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: AppTypography.bodyMedium),
        Text(
          value,
          style: isMonospace
              ? AppTypography.labelMedium.copyWith(fontFamily: 'monospace', color: AppColors.textPrimary)
              : AppTypography.labelMedium.copyWith(color: AppColors.textPrimary),
        ),
      ],
    );
  }
}

