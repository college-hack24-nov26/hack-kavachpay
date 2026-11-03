import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../providers/vault_provider.dart';
import '../../widgets/credential_tile.dart';
import '../../widgets/kavach_card.dart';

class VaultScreen extends ConsumerStatefulWidget {
  const VaultScreen({super.key});

  @override
  ConsumerState<VaultScreen> createState() => _VaultScreenState();
}

class _VaultScreenState extends ConsumerState<VaultScreen> {
  String _selectedCategory = 'ALL';

  @override
  Widget build(BuildContext context) {
    final credentialsAsync = ref.watch(credentialsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Ghost-Vault'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: AppColors.textPrimary),
            onPressed: () => ref.refresh(credentialsProvider),
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Zero-Knowledge Predicate Vault',
                  style: AppTypography.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  'Your credentials remain decoupled on this client. Prove attributes without disclosing underlying documents.',
                  style: AppTypography.bodyMedium,
                ),
                const SizedBox(height: 14),

                // Category Filter Pills
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _categoryFilterChip('ALL', 'All (3)'),
                      const SizedBox(width: 8),
                      _categoryFilterChip('IDENTITY', 'Identity (1)'),
                      const SizedBox(width: 8),
                      _categoryFilterChip('KYC', 'KYC (1)'),
                      const SizedBox(width: 8),
                      _categoryFilterChip('INCOME', 'Income (1)'),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          const Divider(),

          Expanded(
            child: credentialsAsync.when(
              data: (credentials) {
                final filtered = _selectedCategory == 'ALL'
                    ? credentials
                    : credentials.where((c) => c.category.toUpperCase() == _selectedCategory).toList();

                if (filtered.isEmpty) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.folder_open, size: 48, color: AppColors.textHint),
                          const SizedBox(height: 12),
                          Text('No credentials in this category', style: AppTypography.titleMedium),
                          const SizedBox(height: 6),
                          Text(
                            'Only authenticated, cryptographically signed credentials appear here.',
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
                  itemCount: filtered.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 14),
                  itemBuilder: (context, index) {
                    final cred = filtered[index];
                    return CredentialTile(
                      credential: cred,
                      onTap: () => context.go('/vault/${cred.id}'),
                    );
                  },
                );
              },
              loading: () => const Center(
                child: CircularProgressIndicator(color: AppColors.brandGreen),
              ),
              error: (err, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: KavachCard(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.error_outline, color: AppColors.danger, size: 36),
                        const SizedBox(height: 12),
                        Text('Unable to retrieve Ghost-Vault credentials', style: AppTypography.labelLarge),
                        const SizedBox(height: 4),
                        Text('$err', style: AppTypography.caption, textAlign: TextAlign.center),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _categoryFilterChip(String key, String label) {
    final isSelected = _selectedCategory == key;
    return InkWell(
      onTap: () => setState(() => _selectedCategory = key),
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.brandGreen : AppColors.card,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.brandGreen : AppColors.border,
            width: 1,
          ),
        ),
        child: Text(
          label,
          style: AppTypography.labelMedium.copyWith(
            color: isSelected ? Colors.white : AppColors.textSecondary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          ),
        ),
      ),
    );
  }
}

