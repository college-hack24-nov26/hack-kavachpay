import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/kavach_card.dart';
import '../../widgets/status_badge.dart';
import '../../widgets/kavach_button.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final user = authState.user;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Settings & Security'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile Card
            KavachCard(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppColors.brandGreen,
                    child: Text(
                      user?.fullName.isNotEmpty == true ? user!.fullName[0] : 'A',
                      style: const TextStyle(fontSize: 22, color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(user?.fullName ?? 'Aarav Mehta', style: AppTypography.titleMedium),
                        const SizedBox(height: 2),
                        Text(user?.email ?? 'user@kavachsetu.demo', style: AppTypography.caption),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.brandTint,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            'User ID: ${user?.userCode ?? 'KVS-001'}',
                            style: AppTypography.caption.copyWith(
                              fontFamily: 'monospace',
                              color: AppColors.brandGreen,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 22),

            // Profile & Account Details
            Text('Account Information', style: AppTypography.titleMedium),
            const SizedBox(height: 8),
            KavachCard(
              child: Column(
                children: [
                  _infoItem('Registered Phone', user?.phoneMasked ?? '+91 ••••• ••421'),
                  const Divider(),
                  _infoItem('Verification Tier', 'Stage 1 Demo Sandbox'),
                  const Divider(),
                  _infoItem('Account Status', 'Active & Self-Custodial'),
                ],
              ),
            ),

            const SizedBox(height: 22),

            // Real Security Information
            Text('Security Infrastructure', style: AppTypography.titleMedium),
            const SizedBox(height: 4),
            Text('Verified architectural guarantees of the current implementation.', style: AppTypography.bodyMedium),
            const SizedBox(height: 8),
            KavachCard(
              child: Column(
                children: [
                  _securityItem('Password Hashing', 'Bcrypt (12 Rounds Adaptive Cost)', Icons.lock_outline),
                  const Divider(),
                  _securityItem('Vault Key Storage', 'Client Encrypted Decoupled Store', Icons.shield_outlined),
                  const Divider(),
                  _securityItem('Session Security', 'HMAC-SHA256 Signed Bearer Token', Icons.vpn_key_outlined),
                  const Divider(),
                  _securityItem('Zero-Exposure Guarantee', 'Raw statements never saved on servers', Icons.visibility_off_outlined),
                ],
              ),
            ),

            const SizedBox(height: 22),

            // Privacy & Synthetic Notice
            Text('Privacy & Compliance Policy', style: AppTypography.titleMedium),
            const SizedBox(height: 8),
            KavachCard(
              backgroundColor: AppColors.cardSubtle,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.policy_outlined, size: 18, color: AppColors.brandGreen),
                      SizedBox(width: 8),
                      Text('Stage 1 Sandbox Notice', style: AppTypography.labelMedium),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'KavachSetu operates on the principle of "Prove, Don\'t Share". All credentials in this Stage 1 release are synthetic demo assets and do not connect to live UIDAI/PAN/Account Aggregator APIs.',
                    style: AppTypography.caption,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 28),

            // Logout Button
            KavachButton(
              label: 'Sign Out of Ghost-Vault',
              variant: ButtonVariant.secondary,
              icon: Icons.logout,
              onPressed: () async {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Confirm Sign Out'),
                    content: const Text('Are you sure you want to terminate your active Ghost-Vault session?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pop(ctx, true),
                        child: Text(
                          'Sign Out',
                          style: TextStyle(color: AppColors.danger),
                        ),
                      ),
                    ],
                  ),
                );

                if (confirm == true) {
                  await ref.read(authProvider.notifier).logout();
                  if (context.mounted) {
                    context.go('/login');
                  }
                }
              },
            ),

            const SizedBox(height: 20),
            Center(
              child: Text(
                'KavachSetu v1.0.0-stage1 (Build 2026.11)',
                style: AppTypography.caption,
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _infoItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: AppTypography.bodyMedium),
          Text(value, style: AppTypography.labelMedium.copyWith(color: AppColors.textPrimary)),
        ],
      ),
    );
  }

  Widget _securityItem(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.brandGreen),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: AppTypography.labelMedium.copyWith(color: AppColors.textPrimary)),
                Text(value, style: AppTypography.caption),
              ],
            ),
          ),
          const StatusBadge(label: 'ACTIVE', type: BadgeType.success),
        ],
      ),
    );
  }
}

