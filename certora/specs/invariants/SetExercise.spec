/* Verification of `Set` library */
methods {
    function insert(address) external returns (bool) envfree;
    function remove(address) external returns (bool) envfree;
    function get(uint8) external returns (address) envfree;
    function contains(address) external returns (bool) envfree;
    function length() external returns (uint8) envfree;
}


/// @title Elements in set are unique
invariant uniqueElements(uint8 i, uint8 j)
    // TODO


/// @title The length of the set can change at most by 1
rule setLengthChangedByOne(method f) {
    // TODO
}


/// @title Length is increased only by insert and decreased only by remove
/// Meaning:
/// - If the length increased then `insert` was called
/// - If the length decreased then `remove` was called
rule setLengthIncreaseDecrease(method f) {
    // TODO
}
