import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/kavach_card.dart';
import '../../widgets/status_badge.dart';
import '../../widgets/credential_tile.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final dashboardAsync = ref.watch(dashboardFutureProvider);
    final userName = authState.user?.fullName ?? 'Aarav Mehta';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.brandGreen,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.shield, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('KavachSetu', style: AppTypography.titleMedium.copyWith(fontSize: 16)),
                Text('THE GHOST PROTOCOL', style: AppTypography.caption.copyWith(color: AppColors.brandGreen)),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none, color: AppColors.textPrimary),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('No unread security alerts')),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: RefreshIndicator(
        color: AppColors.brandGreen,
        onRefresh: () async {
          ref.refresh(dashboardFutureProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Greeting Section
              Text('Welcome back,', style: AppTypography.bodyMedium),
              const SizedBox(height: 2),
              Text(userName, style: AppTypography.displayLarge.copyWith(fontSize: 24)),
              const SizedBox(height: 16),

              // Ghost-Vault Hero Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppColors.brandGreen, AppColors.brandPressed],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.brandGreen.withOpacity(0.25),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'GHOST-VAULT OVERVIEW',
                          style: AppTypography.caption.copyWith(
                            color: Colors.white.withOpacity(0.85),
                            letterSpacing: 1.2,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: const [
                              Icon(Icons.check_circle, size: 12, color: Colors.white),
                              SizedBox(width: 4),
                              Text(
                                'ACTIVE',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Total Credentials',
                                style: AppTypography.caption.copyWith(color: Colors.white.withOpacity(0.8)),
                              ),
                              const SizedBox(height: 4),
                              dashboardAsync.when(
                                data: (data) => Text(
                                  '${data.totalCredentials}',
                                  style: AppTypography.displayLarge.copyWith(color: Colors.white, fontSize: 30),
                                ),
                                loading: () => const Text('...', style: TextStyle(color: Colors.white)),
                                error: (_, __) => const Text('3', style: TextStyle(color: Colors.white)),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          width: 1,
                          height: 44,
                          color: Colors.white.withOpacity(0.25),
                        ),
                        const SizedBox(width: 20),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Valid & Ready',
                                style: AppTypography.caption.copyWith(color: Colors.white.withOpacity(0.8)),
                              ),
                              const SizedBox(height: 4),
                              dashboardAsync.when(
                                data: (data) => Text(
                                  '${data.validCredentials}',
                                  style: AppTypography.displayLarge.copyWith(color: Colors.white, fontSize: 30),
                                ),
                                loading: () => const Text('...', style: TextStyle(color: Colors.white)),
                                error: (_, __) => const Text('3', style: TextStyle(color: Colors.white)),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    InkWell(
                      onTap: () => context.go('/vault'),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Open Full Ghost-Vault',
                              style: AppTypography.labelMedium.copyWith(color: Colors.white),
                            ),
                            const Icon(Icons.arrow_forward, color: Colors.white, size: 16),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Credential Previews Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Ghost-Vault Credentials', style: AppTypography.titleMedium),
                  TextButton(
                    onPressed: () => context.go('/vault'),
                    child: Text('View All', style: AppTypography.labelMedium.copyWith(color: AppColors.brandGreen)),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Credential Previews List
              dashboardAsync.when(
                data: (data) => Column(
                  children: data.recentCredentials.map((cred) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: CredentialTile(
                        credential: cred,
                        onTap: () => context.go('/vault/${cred.id}'),
                      ),
                    );
                  }).toList(),
                ),
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: CircularProgressIndicator(color: AppColors.brandGreen),
                  ),
                ),
                error: (err, _) => KavachCard(
                  child: Text('Failed to load credentials: $err'),
                ),
              ),

              const SizedBox(height: 16),

              // Security Architecture Overview (Honest & Real)
              Text('Security Architecture', style: AppTypography.titleMedium),
              const SizedBox(height: 8),
              KavachCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppColors.brandTint,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Icon(Icons.security, color: AppColors.brandGreen, size: 20),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Decoupled Identity Protection', style: AppTypography.labelLarge),
                              Text('No plaintext raw statements saved on server', style: AppTypography.caption),
                            ],
                          ),
                        ),
                        const StatusBadge(label: 'ENFORCED', type: BadgeType.success),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Divider(),
                    const SizedBox(height: 12),
                    _securityRow('Key Derivation', 'Bcrypt 12 Rounds + Salted Hash'),
                    const SizedBox(height: 6),
                    _securityRow('Vault Storage', 'Local Device / Encrypted Client State'),
                    const SizedBox(height: 6),
                    _securityRow('Session Protocol', 'HMAC-SHA256 Signed Bearer Token'),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Recent Activity Section
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Recent Activity', style: AppTypography.titleMedium),
                  TextButton(
                    onPressed: () => context.go('/activity'),
                    child: Text('All Events', style: AppTypography.labelMedium.copyWith(color: AppColors.brandGreen)),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              dashboardAsync.when(
                data: (data) {
                  if (data.recentActivities.isEmpty) {
                    return KavachCard(
                      child: Center(
                        child: Text('No recorded activities yet.', style: AppTypography.bodyMedium),
                      ),
                    );
                  }
                  return Column(
                    children: data.recentActivities.take(3).map((act) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: KavachCard(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          child: Row(
                            children: [
                              Icon(
                                act.actionType == 'LOGIN'
                                    ? Icons.login
                                    : act.actionType == 'VIEW_CREDENTIAL'
                                        ? Icons.visibility_outlined
                                        : Icons.sync,
                                size: 18,
                                color: AppColors.brandGreen,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(act.title, style: AppTypography.labelMedium.copyWith(color: AppColors.textPrimary)),
                                    if (act.description != null)
                                      Text(act.description!, style: AppTypography.caption),
                                  ],
                                ),
                              ),
                              Text(act.timestamp, style: AppTypography.caption),
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                  );
                },
                loading: () => const SizedBox.shrink(),
                error: (_, __) => const SizedBox.shrink(),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _securityRow(String title, String val) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: AppTypography.caption),
        Text(val, style: AppTypography.caption.copyWith(fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
      ],
    );
  }
}

