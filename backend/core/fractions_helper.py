from fractions import Fraction
from typing import List, Tuple, Optional


def create_identity_matrix(n: int) -> List[List[Fraction]]:
    """Creates an n x n identity matrix with Fraction entries."""
    return [[Fraction(1, 1) if i == j else Fraction(0, 1) for j in range(n)] for i in range(n)]


def matrix_vector_mult(matrix: List[List[Fraction]], vector: List[Fraction]) -> List[Fraction]:
    """Computes matrix * vector for exact Fraction entries."""
    result = []
    for row in matrix:
        s = Fraction(0, 1)
        for a, b in zip(row, vector):
            s += a * b
        result.append(s)
    return result


def vector_matrix_mult(vector: List[Fraction], matrix: List[List[Fraction]]) -> List[Fraction]:
    """Computes vector^T * matrix (row vector times matrix)."""
    num_cols = len(matrix[0])
    result = []
    for j in range(num_cols):
        s = Fraction(0, 1)
        for i in range(len(vector)):
            s += vector[i] * matrix[i][j]
        result.append(s)
    return result


def dot_product(v1: List[Fraction], v2: List[Fraction]) -> Fraction:
    """Dot product between two vectors of Fractions."""
    return sum(a * b for a, b in zip(v1, v2))


def matrix_mult(A: List[List[Fraction]], B: List[List[Fraction]]) -> List[List[Fraction]]:
    """Computes A * B for exact Fraction matrices."""
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])
    
    result = [[Fraction(0, 1) for _ in range(cols_B)] for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            s = Fraction(0, 1)
            for k in range(cols_A):
                s += A[i][k] * B[k][j]
            result[i][j] = s
    return result


def invert_matrix_exact(matrix: List[List[Fraction]]) -> Optional[List[List[Fraction]]]:
    """
    Inverts an n x n square matrix with Fraction entries using Gauss-Jordan elimination.
    Returns None if the matrix is singular.
    """
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("La matriz debe ser cuadrada para invertirse.")
    
    # Augment matrix with Identity
    aug = [
        [Fraction(matrix[i][j]) for j in range(n)] + [Fraction(1 if i == k else 0, 1) for k in range(n)]
        for i in range(n)
    ]
    
    # Gauss-Jordan elimination
    for col in range(n):
        # Pivot search: find non-zero row
        pivot_row = None
        for r in range(col, n):
            if aug[r][col] != Fraction(0, 1):
                pivot_row = r
                break
        
        if pivot_row is None:
            # Singular matrix
            return None
        
        # Swap rows if needed
        if pivot_row != col:
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        
        pivot_val = aug[col][col]
        
        # Normalize pivot row
        for c in range(2 * n):
            aug[col][c] = aug[col][c] / pivot_val
        
        # Eliminate in all other rows
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                if factor != Fraction(0, 1):
                    for c in range(2 * n):
                        aug[r][c] = aug[r][c] - factor * aug[col][c]
    
    # Extract right side
    inv = [[aug[i][n + j] for j in range(n)] for i in range(n)]
    return inv
