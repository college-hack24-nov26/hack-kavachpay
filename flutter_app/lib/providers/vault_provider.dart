import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/credential.dart';
import 'auth_provider.dart';

final credentialsProvider = FutureProvider.autoDispose<List<CredentialModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getCredentials();
});

final credentialDetailProvider = FutureProvider.autoDispose.family<CredentialModel, String>((ref, id) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getCredentialDetail(id);
});

