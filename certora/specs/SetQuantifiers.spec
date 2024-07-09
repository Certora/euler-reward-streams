/* Quantifiers examples for `Set` library */
methods {
    function insert(address) external returns (bool) envfree;
    function remove(address) external returns (bool) envfree;
    function get(uint8) external returns (address) envfree;
    function contains(address) external returns (bool) envfree;
    function length() external returns (uint8) envfree;
}

/// @title Same as the `length()`
definition numElements() returns uint8 = currentContract.setStorage.numElements;

/// @title The element at the i'th index
/// @notice Unlike `get` this returns the element at `i`, NOT the element at `i - 1`!
definition getElement(uint8 i) returns address = (
    i == 0 ?
    currentContract.setStorage.firstElement :
    currentContract.setStorage.elements[i].value
);


/// @title Elements in set are unique
invariant uniqueElements()
    forall uint8 i. forall uint8 j. (
        (0 <= i && i < j && j < numElements()) => getElement(i) != getElement(j)
    );
