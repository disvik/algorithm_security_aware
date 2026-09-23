class CryptoPolicy:
    """Криптографическая политика распределенной сети."""

    def __init__(
        self,
        required_algorithm="AES-256",
        minimum_security_level=3,
        policy_version=2
    ):
        self.required_algorithm = required_algorithm
        self.minimum_security_level = minimum_security_level
        self.policy_version = policy_version

    def is_algorithm_compliant(self, node):
        return node.crypto_algorithm == self.required_algorithm

    def is_security_level_compliant(self, node):
        return node.crypto_security_level >= self.minimum_security_level

    def is_policy_version_current(self, node):
        return node.crypto_policy_version == self.policy_version

    def is_key_valid(self, node):
        return node.key_valid

    def evaluate_node(self, node):
        """
        Возвращает:
        VALID          - полное соответствие политике;
        TRANSITIONAL   - корректная криптографическая конфигурация,
                         но старая версия политики;
        NON_COMPLIANT  - несоответствие требованиям.
        """
        if not self.is_key_valid(node):
            return "NON_COMPLIANT"

        algorithm_ok = self.is_algorithm_compliant(node)
        security_level_ok = self.is_security_level_compliant(node)
        version_current = self.is_policy_version_current(node)

        if algorithm_ok and security_level_ok and version_current:
            return "VALID"

        if (
            algorithm_ok
            and security_level_ok
            and node.crypto_policy_version < self.policy_version
        ):
            return "TRANSITIONAL"

        return "NON_COMPLIANT"

    def apply_to_node(self, node):
        node.crypto_state = self.evaluate_node(node)
        return node.crypto_state

    def __str__(self):
        return (
            f"CryptoPolicy(algorithm={self.required_algorithm}, "
            f"minimum_security_level={self.minimum_security_level}, "
            f"version={self.policy_version})"
        )
