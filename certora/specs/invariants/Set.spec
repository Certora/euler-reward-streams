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
    (0 < i && i < j && j <= length()) => get(i) != get(j)
    {
        preserved remove(address element) {
            requireInvariant uniqueElements(i, length());
            requireInvariant uniqueElements(j, length());
        }
    }


/// @title The length of the set can change at most by 1
rule setLengthChangedByOne(method f) {
    uint8 preLen = length();

    env e;
    calldataarg args;
    f(e, args);

    uint8 postLen = length();
    mathint diff = postLen - preLen;
    assert (diff >= -1 && diff <= 1, "length change is at most 1");
}


/// @title Length is increased only by insert and decreased only by remove
rule setLengthIncreaseDecrease(method f) {
    uint8 preLen = length();

    env e;
    calldataarg args;
    f(e, args);

    uint8 postLen = length();
    assert (
         postLen > preLen => f.selector == sig:insert(address).selector,
        "length is incresed only by insert"
    );
    assert (
        postLen < preLen => f.selector == sig:remove(address).selector,
        "length is decreased only by remove"
    );
}
