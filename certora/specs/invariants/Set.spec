/* Verification of `Set` library */
methods {
    function insert(address) external returns (bool) envfree;
    function remove(address) external returns (bool) envfree;
    function get(uint8) external returns (address) envfree;
    function contains(address) external returns (bool) envfree;
    function length() external returns (uint8) envfree;
}


/// @title Elements in set are unique - this rule is violated (missing preserved block)
invariant uniqueElementsNoPreserved(uint8 i, uint8 j)
    (0 < i && i < j && j <= length()) => get(i) != get(j);


/// @title Elements in set are unique
invariant uniqueElements(uint8 i, uint8 j)
    (0 < i && i < j && j <= length()) => get(i) != get(j)
    {
        preserved remove(address element) {
            requireInvariant uniqueElements(i, length());
            requireInvariant uniqueElements(j, length());
        }
    }
