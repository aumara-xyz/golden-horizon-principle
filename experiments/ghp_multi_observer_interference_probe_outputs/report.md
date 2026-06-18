# GHP Multi-Observer Interference Probe

Status: synthetic toy telemetry only.

This tests the two-ear / two-node idea in a bounded way: two separate observer records can reconstruct more hidden state when paired correctly, and fail when mismatched.

It does not prove that reality is literally made from observer interference.

## Results

### MOI-001: pass

- Metric: paired_x_mae; single_x_mae; shuffled_x_mae; paired_y_mae; single_y_mae; shuffled_y_mae; paired_side_acc; single_side_acc; shuffled_side_acc
- Value: 0.0552; 1.0101; 1.5171; 0.0341; 0.4587; 0.8859; 0.9865; 0.5085; 0.6145
- Null hypothesis: Paired observers do not reconstruct hidden source state better than one observer or shuffled pairing.
- Safest read: Correctly paired bounded observers reconstruct more hidden geometry than either single observer or a mismatched observer stream.
- Falsifier: Single-observer or shuffled-pair controls match the paired reconstruction.

### MOI-002: policy

- Metric: authority_status
- Value: interference_is_evidence_not_authority
- Null hypothesis: n/a
- Safest read: The paired estimate can inform memory or confidence only after both observer receipts verify. It must not bypass gate authorization.
- Falsifier: Any implementation lets phase/interference directly authorize action.

## Aukora Translation

```text
node A observation + node B observation + verified pairing
  -> shared estimate
  -> receipt
  -> optional memory / learning consequence
```

Hard rule:

```text
Interference may be evidence.
Interference may be memory.
Interference may never be authority.
```

## Next Test

Move from synthetic distance observations to two live Aukora demo nodes watching the same bounded event stream. Compare paired receipts against single-node and shuffled-pair controls.
