import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/activity_provider.dart';
import '../../widgets/kavach_card.dart';
import '../../widgets/status_badge.dart';

class ActivityScreen extends ConsumerWidget {
  const ActivityScreen({super.key});

  IconData _iconForAction(String action) {
    switch (action.toUpperCase()) {
      case 'LOGIN':
        return Icons.login_rounded;
      case 'LOGOUT':
        return Icons.logout_rounded;
      case 'VIEW_CREDENTIAL':
        return Icons.visibility_outlined;
      case 'VAULT_INITIALIZED':
        return Icons.shield_outlined;
      default:
        return Icons.notifications_active_outlined;
    }
  }

  BadgeType _badgeTypeForAction(String action) {
    switch (action.toUpperCase()) {
      case 'LOGIN':
        return BadgeType.success;
      case 'LOGOUT':
        return BadgeType.neutral;
      case 'VIEW_CREDENTIAL':
        return BadgeType.info;
      default:
        return BadgeType.neutral;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activityAsync = ref.watch(activityProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Activity History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: AppColors.textPrimary),
            onPressed: () => ref.refresh(activityProvider),
          ),
        ],
      ),
      body: RefreshIndicator(
        color: AppColors.brandGreen,
        onRefresh: () async => ref.refresh(activityProvider),
        child: activityAsync.when(
          data: (activities) {
            if (activities.isEmpty) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.history, size: 48, color: AppColors.textHint),
                      const SizedBox(height: 12),
                      Text('No Activity Logged', style: AppTypography.titleMedium),
                      const SizedBox(height: 6),
                      Text(
                        'Every authentication and credential access is cryptographically recorded here.',
                        style: AppTypography.bodyMedium,
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              itemCount: activities.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final act = activities[index];
                return KavachCard(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppColors.cardSubtle,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: Icon(
                          _iconForAction(act.actionType),
                          color: AppColors.brandGreen,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    act.title,
                                    style: AppTypography.labelLarge,
                                  ),
                                ),
                                StatusBadge(
                                  label: act.actionType,
                                  type: _badgeTypeForAction(act.actionType),
                                ),
                              ],
                            ),
                            if (act.description != null && act.description!.isNotEmpty) ...[
                              const SizedBox(height: 4),
                              Text(act.description!, style: AppTypography.bodyMedium),
                            ],
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  act.timestamp,
                                  style: AppTypography.caption,
                                ),
                                Text(
                                  act.ipMasked,
                                  style: AppTypography.caption.copyWith(fontFamily: 'monospace'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            );
          },
          loading: () => const Center(child: CircularProgressIndicator(color: AppColors.brandGreen)),
          error: (err, _) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: KavachCard(
                child: Text('Unable to load activity logs: $err'),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

